import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { useRole } from "@/contexts/RoleContext";
import { AlertTriangle, Clock, ChevronRight, Check, X } from "lucide-react";

interface Alert {
  id: number;
  title: string;
  time: string;
  severity: "low" | "medium" | "high";
  confidence: number;
}

const severityStyles = {
  low: "bg-secondary text-secondary-foreground",
  medium: "bg-warning/15 text-warning",
  high: "bg-calm-alert/15 text-calm-alert",
};

export function AlertsPanel() {
  const { role } = useRole();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [seedingDemo, setSeedingDemo] = useState(false);

  const loadAlerts = useCallback(async (isMounted = true) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/alerts?role=${role}`);
      const result: Alert[] = await response.json();

      if (isMounted) {
        setAlerts(result);
      }
    } catch (error) {
      console.error("Failed to load alerts", error);
    } finally {
      if (isMounted) {
        setLoading(false);
      }
    }
  }, [role]);

  useEffect(() => {
    let isMounted = true;

    loadAlerts(isMounted);

    return () => {
      isMounted = false;
    };
  }, [loadAlerts]);

  const handleAction = async (id: number, action: "approve" | "reject") => {
    try {
      await fetch("http://127.0.0.1:8000/alerts/action", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ alert_id: id, action }),
      });

      setAlerts((prev) => prev.filter((alert) => alert.id !== id));
    } catch (error) {
      console.error(`Failed to ${action} alert`, error);
    }
  };

  const handleSeedDemoAlert = async () => {
    try {
      setSeedingDemo(true);
      await fetch(`http://127.0.0.1:8000/alerts/demo/seed?role=${role}`, {
        method: "POST",
      });
      await loadAlerts(true);
    } catch (error) {
      console.error("Failed to seed demo alert", error);
    } finally {
      setSeedingDemo(false);
    }
  };

  return (
    <div className="bg-card rounded-xl p-5 shadow-card border border-border animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-heading font-semibold text-card-foreground">Alerts</h3>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground">{alerts.length} active</span>
          {role === "supervisor" ? (
            <Button size="sm" variant="outline" className="h-7 text-xs" onClick={handleSeedDemoAlert} disabled={seedingDemo}>
              {seedingDemo ? "Seeding..." : "Generate Demo Alert"}
            </Button>
          ) : null}
        </div>
      </div>
      <div className="space-y-3">
        {loading ? (
          <div className="p-3.5 rounded-lg border border-border bg-background text-sm text-muted-foreground">
            Loading...
          </div>
        ) : null}
        {!loading && alerts.length === 0 ? (
          <div className="p-3.5 rounded-lg border border-border bg-background text-sm text-muted-foreground">
            No active alerts right now.
          </div>
        ) : null}
        {alerts.map((alert) => (
          <div key={alert.id} className="p-3.5 rounded-lg border border-border bg-background hover:shadow-card transition-shadow">
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-start gap-2.5">
                <AlertTriangle className="w-4 h-4 mt-0.5 text-calm-alert shrink-0" />
                <div>
                  <p className="text-sm font-medium text-card-foreground">{alert.title}</p>
                  <div className="flex items-center gap-2 mt-1.5">
                    <span className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Clock className="w-3 h-3" />
                      {alert.time}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${severityStyles[alert.severity]}`}>
                      {alert.severity}
                    </span>
                  </div>
                  {role !== "family" && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Confidence: {(alert.confidence * 100).toFixed(0)}%
                    </p>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2 mt-3">
              <Button variant="outline" size="sm" className="text-xs h-7 gap-1">
                View Details <ChevronRight className="w-3 h-3" />
              </Button>
              {role === "supervisor" && (
                <>
                  <Button
                    size="sm"
                    className="text-xs h-7 gap-1 bg-success hover:bg-success/90 text-success-foreground"
                    onClick={() => handleAction(alert.id, "approve")}
                  >
                    <Check className="w-3 h-3" /> Approve
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-xs h-7 gap-1 text-calm-alert border-calm-alert/30 hover:bg-calm-alert/10"
                    onClick={() => handleAction(alert.id, "reject")}
                  >
                    <X className="w-3 h-3" /> Reject
                  </Button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
