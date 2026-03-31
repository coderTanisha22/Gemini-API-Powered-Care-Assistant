import { Shield, AlertCircle } from "lucide-react";

interface StatusSummaryProps {
  status: "normal" | "attention";
}

export function StatusSummary({ status }: StatusSummaryProps) {
  const isNormal = status === "normal";

  return (
    <div
      className={`rounded-xl p-5 shadow-card border animate-fade-in ${
        isNormal
          ? "bg-success/8 border-success/20"
          : "bg-warning/8 border-warning/20"
      }`}
    >
      <div className="flex items-center gap-3">
        {isNormal ? (
          <div className="w-10 h-10 rounded-full bg-success/15 flex items-center justify-center">
            <Shield className="w-5 h-5 text-success" />
          </div>
        ) : (
          <div className="w-10 h-10 rounded-full bg-warning/15 flex items-center justify-center">
            <AlertCircle className="w-5 h-5 text-warning" />
          </div>
        )}
        <div>
          <p className="text-sm text-muted-foreground">Overall Status</p>
          <p className={`text-lg font-heading font-semibold ${isNormal ? "text-success" : "text-warning"}`}>
            {isNormal ? "Activity: Normal" : "Needs Attention"}
          </p>
        </div>
      </div>
    </div>
  );
}
