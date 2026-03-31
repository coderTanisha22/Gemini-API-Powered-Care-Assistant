import { useEffect, useState } from "react";
import { Brain, Mic } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Insight {
  summary: string;
  confidence: number;
}

export function AIExplanation() {
  const [insight, setInsight] = useState<Insight | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const loadInsight = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/insight");
        const result: Insight = await response.json();

        if (isMounted) {
          setInsight(result);
        }
      } catch (error) {
        console.error("Failed to load insight", error);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadInsight();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="bg-primary/5 rounded-xl p-5 shadow-card border border-primary/15 animate-fade-in">
      <div className="flex items-center gap-2 mb-3">
        <Brain className="w-5 h-5 text-primary" />
        <h3 className="font-heading font-semibold text-card-foreground">AI Insight</h3>
      </div>
      <p className="text-base leading-relaxed text-foreground/85">
        {loading ? "Loading..." : insight?.summary}
      </p>
      {!loading && insight ? (
        <p className="text-xs text-muted-foreground mt-3">Confidence: {(insight.confidence * 100).toFixed(0)}%</p>
      ) : null}
      <div className="flex items-center gap-3 mt-4">
        <Button variant="outline" size="sm" className="gap-2 text-xs">
          <Mic className="w-3.5 h-3.5" />
          Ask about today's activity
        </Button>
      </div>
    </div>
  );
}
