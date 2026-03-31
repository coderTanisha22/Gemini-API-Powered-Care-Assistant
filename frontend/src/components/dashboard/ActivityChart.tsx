import { useEffect, useState } from "react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface ActivityResponse {
  timeline: number[];
  status: string;
}

const timeLabels = ["6:00", "7:00", "8:00", "9:00", "10:00", "11:00", "12:00"];

export function ActivityChart() {
  const [data, setData] = useState<{ time: string; activity: number }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const loadActivity = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/activity");
        const result: ActivityResponse = await response.json();

        if (!isMounted) {
          return;
        }

        setData(
          result.timeline.map((value, index) => ({
            time: timeLabels[index] ?? `${index + 1}:00`,
            activity: value,
          })),
        );
      } catch (error) {
        console.error("Failed to load activity data", error);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadActivity();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="bg-card rounded-xl p-5 shadow-card border border-border animate-fade-in">
      <h3 className="font-heading font-semibold text-card-foreground mb-4">Activity Overview</h3>
      <div className="h-56">
        {loading ? (
          <div className="h-full flex items-center justify-center text-sm text-muted-foreground">Loading...</div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="activityGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="hsl(168, 55%, 38%)" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="hsl(168, 55%, 38%)" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(150, 15%, 88%)" />
              <XAxis dataKey="time" tick={{ fontSize: 12, fill: "hsl(200, 10%, 50%)" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 12, fill: "hsl(200, 10%, 50%)" }} axisLine={false} tickLine={false} label={{ value: "Intensity", angle: -90, position: "insideLeft", style: { fontSize: 11, fill: "hsl(200, 10%, 50%)" } }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(0, 0%, 100%)",
                  border: "1px solid hsl(150, 15%, 88%)",
                  borderRadius: "0.5rem",
                  fontSize: "0.8rem",
                }}
              />
              <Area type="monotone" dataKey="activity" stroke="hsl(168, 55%, 38%)" strokeWidth={2.5} fill="url(#activityGradient)" />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
