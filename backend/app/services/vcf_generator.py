"""
VCF Generator Service

Generates VCF (vCard) files from contact pool with serial naming.
Serial naming logic:
- Each contact gets a name like "LEG001"
- The serial number increments every N contacts (default: 25)
- This allows agents to add 25 contacts at a time with the same name prefix
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contacts import ContactPool, VcfBatch, VcfBatchStatus


class VcfGeneratorService:
    """Service for generating VCF files from contact pool."""
    
    STORAGE_PATH = "storage/vcf"
    
    def __init__(self):
        # Ensure storage directory exists
        os.makedirs(self.STORAGE_PATH, exist_ok=True)
    
    def generate_vcard(self, name: str, phone: str) -> str:
        """Generate a single vCard entry."""
        # Clean phone number (remove spaces, ensure + prefix for international)
        phone = phone.strip().replace(" ", "").replace("-", "")
        if not phone.startswith("+"):
            # Assume Israeli number if no country code
            if phone.startswith("0"):
                phone = "+972" + phone[1:]
            else:
                phone = "+" + phone
        
        return f"""BEGIN:VCARD
VERSION:3.0
FN:{name}
TEL;TYPE=CELL:{phone}
END:VCARD
"""
    
    def generate_serial_name(self, prefix: str, serial: int) -> str:
        """
        Generate serial name like 'LEG001', 'LEG002', etc.
        Pads to 3 digits for up to 999 serials.
        """
        return f"{prefix}{serial:03d}"
    
    async def generate_vcf_batch(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        prefix: str = "LEG",
        contacts_per_batch: int = 1500,
        contacts_per_serial: int = 25,
        start_serial: int = 1
    ) -> Optional[VcfBatch]:
        """
        Generate a VCF batch from unassigned contacts in the pool.
        
        Args:
            session: Database session
            tenant_id: Tenant UUID
            prefix: Serial name prefix (e.g., "LEG")
            contacts_per_batch: Max contacts per VCF file
            contacts_per_serial: How many contacts share the same serial name
            start_serial: Starting serial number
        
        Returns:
            VcfBatch object if contacts were available, None otherwise
        """
        # Fetch unassigned contacts
        result = await session.execute(
            select(ContactPool)
            .where(ContactPool.tenant_id == tenant_id)
            .where(ContactPool.is_assigned == False)
            .order_by(ContactPool.uploaded_at)
            .limit(contacts_per_batch)
        )
        contacts = result.scalars().all()
        
        if not contacts:
            return None
        
        # Create VCF batch record
        batch = VcfBatch(
            tenant_id=tenant_id,
            prefix=prefix,
            start_serial=start_serial,
            contacts_per_serial=contacts_per_serial,
            contact_count=len(contacts),
            status=VcfBatchStatus.PENDING.value
        )
        session.add(batch)
        await session.flush()  # Get the batch ID
        
        # Generate VCF content
        vcf_content = ""
        current_serial = start_serial
        contacts_in_current_serial = 0
        
        for contact in contacts:
            # Generate serial name
            serial_name = self.generate_serial_name(prefix, current_serial)
            
            # Add vCard entry
            vcf_content += self.generate_vcard(serial_name, contact.phone)
            
            # Update contact assignment
            contact.vcf_batch_id = batch.id
            contact.is_assigned = True
            
            # Increment serial counter
            contacts_in_current_serial += 1
            if contacts_in_current_serial >= contacts_per_serial:
                current_serial += 1
                contacts_in_current_serial = 0
        
        # Save VCF file
        file_name = f"batch_{batch.id}_{prefix}_{start_serial}.vcf"
        file_path = os.path.join(self.STORAGE_PATH, file_name)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(vcf_content)
        
        # Update batch with file info
        batch.file_path = file_path
        batch.file_name = file_name
        
        await session.commit()
        
        return batch
    
    async def generate_multiple_batches(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        prefix: str = "LEG",
        contacts_per_batch: int = 1500,
        contacts_per_serial: int = 25,
        max_batches: int = 10
    ) -> List[VcfBatch]:
        """
        Generate multiple VCF batches until pool is exhausted or max reached.
        
        Returns:
            List of generated VcfBatch objects
        """
        batches = []
        current_serial = 1
        
        for _ in range(max_batches):
            batch = await self.generate_vcf_batch(
                session=session,
                tenant_id=tenant_id,
                prefix=prefix,
                contacts_per_batch=contacts_per_batch,
                contacts_per_serial=contacts_per_serial,
                start_serial=current_serial
            )
            
            if batch is None:
                break  # No more contacts
            
            batches.append(batch)
            
            # Calculate next starting serial
            # Each batch has (contacts_per_batch / contacts_per_serial) serials
            serials_used = (batch.contact_count + contacts_per_serial - 1) // contacts_per_serial
            current_serial += serials_used
        
        return batches
    
    async def assign_batch_to_agent(
        self,
        session: AsyncSession,
        batch_id: uuid.UUID,
        agent_id: uuid.UUID
    ) -> Optional[VcfBatch]:
        """Assign a pending VCF batch to an agent."""
        result = await session.execute(
            select(VcfBatch).where(VcfBatch.id == batch_id)
        )
        batch = result.scalars().first()
        
        if not batch or batch.status != VcfBatchStatus.PENDING.value:
            return None
        
        batch.agent_id = agent_id
        batch.status = VcfBatchStatus.ASSIGNED.value
        batch.assigned_at = datetime.utcnow()
        
        await session.commit()
        return batch
    
    async def get_agent_batches(
        self,
        session: AsyncSession,
        agent_id: uuid.UUID
    ) -> List[VcfBatch]:
        """Get all VCF batches assigned to an agent."""
        result = await session.execute(
            select(VcfBatch)
            .where(VcfBatch.agent_id == agent_id)
            .order_by(VcfBatch.assigned_at.desc())
        )
        return result.scalars().all()
    
    async def get_pending_batches(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID
    ) -> List[VcfBatch]:
        """Get all pending (unassigned) batches for a tenant."""
        result = await session.execute(
            select(VcfBatch)
            .where(VcfBatch.tenant_id == tenant_id)
            .where(VcfBatch.status == VcfBatchStatus.PENDING.value)
            .order_by(VcfBatch.created_at)
        )
        return result.scalars().all()


# Singleton instance
vcf_generator = VcfGeneratorService()
