import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { ActivityChart } from "@/components/dashboard/ActivityChart";
import { ActivityTimeline } from "@/components/dashboard/ActivityTimeline";
import { AlertsPanel } from "@/components/dashboard/AlertsPanel";
import { AIExplanation } from "@/components/dashboard/AIExplanation";
import { StatusSummary } from "@/components/dashboard/StatusSummary";
import { FamilyView } from "@/components/dashboard/FamilyView";
import { useRole } from "@/contexts/RoleContext";

interface ActivityResponse {
  status: "normal" | "alert";
}

function DashboardContent() {
  const { role } = useRole();
  const [status, setStatus] = useState<"normal" | "attention">("normal");

  useEffect(() => {
    let isMounted = true;

    const loadStatus = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/activity?role=${role}`);
        const result: ActivityResponse = await response.json();

        if (isMounted) {
          setStatus(result.status === "alert" ? "attention" : "normal");
        }
      } catch (error) {
        console.error("Failed to load dashboard status", error);
      }
    };

    loadStatus();
    const timer = window.setInterval(loadStatus, 10000);

    return () => {
      isMounted = false;
      window.clearInterval(timer);
    };
  }, [role]);

  if (role === "family") {
    return <FamilyView />;
  }

  return (
    <div className="space-y-5 max-w-6xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-heading text-2xl font-bold text-foreground">Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            {role === "supervisor" ? "Supervisor overview — review and manage alerts" : "Monitor activity and insights"}
          </p>
        </div>
      </div>

      <StatusSummary status={status} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <ActivityChart />
        <AIExplanation />
      </div>

      <ActivityTimeline />
      <AlertsPanel />
    </div>
  );
}

export default function Index() {
  return (
    <DashboardLayout>
      <DashboardContent />
    </DashboardLayout>
  );
}
