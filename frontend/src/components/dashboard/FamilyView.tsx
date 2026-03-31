import { Heart, Shield } from "lucide-react";

export function FamilyView() {
  return (
    <div className="max-w-lg mx-auto mt-8 animate-fade-in">
      <div className="bg-card rounded-2xl p-8 shadow-elevated border border-border text-center">
        <div className="w-16 h-16 rounded-full bg-success/15 flex items-center justify-center mx-auto mb-5">
          <Heart className="w-8 h-8 text-success" />
        </div>
        <h2 className="font-heading text-2xl font-semibold text-card-foreground mb-2">
          Everything looks normal
        </h2>
        <p className="text-muted-foreground leading-relaxed">
          Your loved one's activity is within the usual patterns today. The care team is actively monitoring and will reach out if anything needs your attention.
        </p>
        <div className="mt-6 p-4 rounded-xl bg-secondary flex items-center gap-3">
          <Shield className="w-5 h-5 text-primary shrink-0" />
          <p className="text-sm text-secondary-foreground text-left">
            Last check-in: 15 minutes ago. All systems active.
          </p>
        </div>
      </div>
    </div>
  );
}
