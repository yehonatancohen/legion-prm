"""
Contact Pool Service

Handles Excel file parsing and contact pool management.
Supports .xlsx and .xls files with phone numbers.
"""

import os
import uuid
import re
from datetime import datetime
from typing import List, Optional, Tuple
from io import BytesIO
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contacts import ContactPool


class ContactPoolService:
    """Service for managing contact pool from Excel uploads."""
    
    UPLOAD_PATH = "storage/uploads"
    
    def __init__(self):
        os.makedirs(self.UPLOAD_PATH, exist_ok=True)
    
    def clean_phone_number(self, phone: str) -> Optional[str]:
        """
        Clean and validate phone number.
        Returns None if invalid.
        """
        if not phone:
            return None
        
        # Convert to string and strip
        phone = str(phone).strip()
        
        # Remove common formatting characters
        phone = re.sub(r'[\s\-\(\)\.]', '', phone)
        
        # Remove any non-digit characters except leading +
        if phone.startswith('+'):
            phone = '+' + re.sub(r'[^\d]', '', phone[1:])
        else:
            phone = re.sub(r'[^\d]', '', phone)
        
        # Validate length (minimum 7 digits for valid phone)
        digits_only = re.sub(r'[^\d]', '', phone)
        if len(digits_only) < 7 or len(digits_only) > 15:
            return None
        
        # Normalize Israeli numbers
        if phone.startswith('0') and len(phone) == 10:
            # Israeli format: 0501234567 -> +972501234567
            phone = '+972' + phone[1:]
        elif phone.startswith('972'):
            phone = '+' + phone
        elif not phone.startswith('+'):
            # Assume Israeli if no country code
            if len(phone) == 9:  # Missing leading 0
                phone = '+972' + phone
            else:
                phone = '+' + phone
        
        return phone
    
    async def parse_excel_file(
        self,
        file_content: bytes,
        file_name: str
    ) -> Tuple[List[str], List[str], int]:
        """
        Parse Excel file and extract phone numbers.
        
        Args:
            file_content: Raw file bytes
            file_name: Original filename
        
        Returns:
            Tuple of (valid_phones, invalid_entries, total_rows)
        """
        try:
            import openpyxl
        except ImportError:
            raise ImportError("openpyxl is required. Install with: pip install openpyxl")
        
        valid_phones = []
        invalid_entries = []
        
        # Load workbook from bytes
        workbook = openpyxl.load_workbook(BytesIO(file_content), data_only=True)
        sheet = workbook.active
        
        total_rows = 0
        
        for row in sheet.iter_rows(min_row=1):  # Start from row 1 (handle header if exists)
            for cell in row:
                if cell.value is None:
                    continue
                
                total_rows += 1
                raw_value = str(cell.value)
                
                # Skip obvious header cells
                if raw_value.lower() in ['phone', 'phone number', 'טלפון', 'מספר', 'number', 'mobile']:
                    continue
                
                cleaned = self.clean_phone_number(raw_value)
                if cleaned:
                    if cleaned not in valid_phones:  # Deduplicate
                        valid_phones.append(cleaned)
                else:
                    if raw_value.strip():  # Only track non-empty invalid entries
                        invalid_entries.append(raw_value)
        
        return valid_phones, invalid_entries, total_rows
    
    async def upload_contacts(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        file_content: bytes,
        file_name: str
    ) -> dict:
        """
        Upload contacts from Excel file to the pool.
        
        Returns:
            Dict with upload statistics
        """
        valid_phones, invalid_entries, total_rows = await self.parse_excel_file(
            file_content, file_name
        )
        
        # Check for existing phones in pool (for this tenant)
        existing_result = await session.execute(
            select(ContactPool.phone)
            .where(ContactPool.tenant_id == tenant_id)
            .where(ContactPool.phone.in_(valid_phones))
        )
        existing_phones = set(row[0] for row in existing_result)
        
        # Filter out duplicates
        new_phones = [p for p in valid_phones if p not in existing_phones]
        
        # Create contact records
        contacts = []
        for phone in new_phones:
            contact = ContactPool(
                tenant_id=tenant_id,
                phone=phone,
                source_file=file_name,
                uploaded_at=datetime.utcnow()
            )
            contacts.append(contact)
            session.add(contact)
        
        await session.commit()
        
        return {
            "file_name": file_name,
            "total_rows": total_rows,
            "valid_phones": len(valid_phones),
            "new_contacts": len(new_phones),
            "duplicates": len(valid_phones) - len(new_phones),
            "invalid_entries": len(invalid_entries),
            "invalid_samples": invalid_entries[:10]  # Sample of invalid entries
        }
    
    async def get_pool_stats(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID
    ) -> dict:
        """Get statistics about the contact pool."""
        # Total contacts
        total_result = await session.execute(
            select(func.count(ContactPool.id))
            .where(ContactPool.tenant_id == tenant_id)
        )
        total = total_result.scalar() or 0
        
        # Unassigned contacts
        unassigned_result = await session.execute(
            select(func.count(ContactPool.id))
            .where(ContactPool.tenant_id == tenant_id)
            .where(ContactPool.is_assigned == False)
        )
        unassigned = unassigned_result.scalar() or 0
        
        # Assigned contacts
        assigned = total - unassigned
        
        # Contacts by source file
        sources_result = await session.execute(
            select(ContactPool.source_file, func.count(ContactPool.id))
            .where(ContactPool.tenant_id == tenant_id)
            .group_by(ContactPool.source_file)
        )
        sources = [{"file": row[0], "count": row[1]} for row in sources_result]
        
        return {
            "total_contacts": total,
            "assigned": assigned,
            "unassigned": unassigned,
            "assignment_rate": round(assigned / total * 100, 1) if total > 0 else 0,
            "sources": sources
        }
    
    async def get_unassigned_contacts(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0
    ) -> List[ContactPool]:
        """Get unassigned contacts from the pool."""
        result = await session.execute(
            select(ContactPool)
            .where(ContactPool.tenant_id == tenant_id)
            .where(ContactPool.is_assigned == False)
            .order_by(ContactPool.uploaded_at)
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()


# Singleton instance
contact_pool_service = ContactPoolService()
