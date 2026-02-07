
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, CheckCircle, Download, Smartphone, Users } from "lucide-react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const TUTORIAL_STEPS = [
    {
        title: "Welcome to Legion",
        description: "Your comprehensive contact management center.",
        icon: Users,
        content: (
            <div className="space-y-4">
                <p>You play a crucial role in expanding our network. Your primary mission is to manage contact distribution efficiently using WhatsApp.</p>
                <p>This platform will provide you with organized contact batches and track your daily progress.</p>
            </div>
        ),
    },
    {
        title: "Your Daily Mission",
        description: "Consistency is key to our success.",
        icon: CheckCircle,
        content: (
            <div className="space-y-4">
                <div className="bg-secondary/20 p-4 rounded-lg border border-border">
                    <h4 className="font-semibold mb-2">Daily Targets:</h4>
                    <ul className="list-disc list-inside space-y-1">
                        <li>🌞 <strong>Morning:</strong> Add 25 contacts</li>
                        <li>🌙 <strong>Evening:</strong> Add 25 contacts</li>
                        <li>📊 <strong>Report:</strong> Check in here twice a day</li>
                    </ul>
                </div>
                <p className="text-sm text-muted-foreground">Adding contacts in small batches prevents WhatsApp restrictions and ensures steady growth.</p>
            </div>
        ),
    },
    {
        title: "How It Works",
        description: "We've automated the hard part for you.",
        icon: Download,
        content: (
            <div className="space-y-4">
                <p>You will receive a <strong>VCF File</strong> containing 1,500 contacts.</p>
                <ol className="list-decimal list-inside space-y-2">
                    <li>Download the VCF file to your phone</li>
                    <li>Open it to import all contacts at once</li>
                    <li>Contacts are named serially (e.g., <code>LEG001</code>, <code>LEG002</code>)</li>
                    <li>Search for "LEG" in WhatsApp to find them easily</li>
                </ol>
            </div>
        ),
    },
    {
        title: "Ready to Deploy?",
        description: "Let's get you set up with your first batch.",
        icon: Smartphone,
        content: (
            <div className="space-y-4 text-center">
                <p>Click below to access your dashboard and download your first contact batch.</p>
                <p className="font-medium text-primary">Good luck, Agent.</p>
            </div>
        ),
    },
];

export default function TutorialPage() {
    const [currentStep, setCurrentStep] = useState(0);
    const router = useRouter();

    const handleNext = () => {
        if (currentStep < TUTORIAL_STEPS.length - 1) {
            setCurrentStep(currentStep + 1);
        } else {
            // Mark tutorial as complete (in a real app, API call here)
            localStorage.setItem("legion_tutorial_complete", "true");
            router.push("/dashboard");
        }
    };

    const StepIcon = TUTORIAL_STEPS[currentStep].icon;

    return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-background">
            <Card className="w-full max-w-lg shadow-lg border-2 border-primary/10">
                <CardHeader className="text-center pb-2">
                    <div className="mx-auto w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4 text-primary">
                        <StepIcon size={32} />
                    </div>
                    <CardTitle className="text-2xl font-bold text-foreground">
                        {TUTORIAL_STEPS[currentStep].title}
                    </CardTitle>
                    <CardDescription className="text-base">
                        {TUTORIAL_STEPS[currentStep].description}
                    </CardDescription>
                </CardHeader>

                <CardContent className="pt-4">
                    {TUTORIAL_STEPS[currentStep].content}
                </CardContent>

                <CardFooter className="flex flex-col gap-4">

                    <Button
                        className="w-full h-12 text-lg gap-2"
                        onClick={handleNext}
                    >
                        {currentStep === TUTORIAL_STEPS.length - 1 ? "Enter Dashboard" : "Continue"}
                        {currentStep !== TUTORIAL_STEPS.length - 1 && <ArrowRight size={18} />}
                    </Button>

                    <div className="flex justify-center gap-2">
                        {TUTORIAL_STEPS.map((_, index) => (
                            <div
                                key={index}
                                className={`h-2 w-2 rounded-full transition-colors duration-300 ${index === currentStep ? "bg-primary" : "bg-muted"
                                    }`}
                            />
                        ))}
                    </div>
                </CardFooter>
            </Card>
        </div>
    );
}
