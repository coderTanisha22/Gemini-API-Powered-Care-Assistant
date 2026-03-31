const blocks = [
  { start: "6:00", end: "7:00", active: false },
  { start: "7:00", end: "8:00", active: true },
  { start: "8:00", end: "8:15", active: true },
  { start: "8:15", end: "9:00", active: false },
  { start: "9:00", end: "10:00", active: true },
  { start: "10:00", end: "12:00", active: false },
  { start: "12:00", end: "13:00", active: true },
  { start: "13:00", end: "15:00", active: true },
  { start: "15:00", end: "16:00", active: true },
  { start: "16:00", end: "17:00", active: false },
  { start: "17:00", end: "18:00", active: true },
];

export function ActivityTimeline() {
  return (
    <div className="bg-card rounded-xl p-5 shadow-card border border-border animate-fade-in">
      <h3 className="font-heading font-semibold text-card-foreground mb-4">Activity Timeline</h3>
      <div className="flex gap-0.5 rounded-lg overflow-hidden">
        {blocks.map((block, i) => (
          <div
            key={i}
            className={`h-8 flex-1 transition-colors ${
              block.active ? "bg-success" : "bg-muted"
            }`}
            title={`${block.start}–${block.end}: ${block.active ? "Active" : "Inactive"}`}
          />
        ))}
      </div>
      <div className="flex justify-between mt-2 text-xs text-muted-foreground">
        <span>6:00 AM</span>
        <span>12:00 PM</span>
        <span>6:00 PM</span>
      </div>
      <div className="flex items-center gap-4 mt-3">
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-sm bg-success" />
          <span className="text-xs text-muted-foreground">Active</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-sm bg-muted" />
          <span className="text-xs text-muted-foreground">Inactive</span>
        </div>
      </div>
    </div>
  );
}
