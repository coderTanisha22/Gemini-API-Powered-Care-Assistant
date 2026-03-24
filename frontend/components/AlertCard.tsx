type Props = {
  summary: string;
  severity: number;
};

export default function AlertCard({ summary, severity }: Props) {
  return (
    <div style={{ border: "1px solid gray", padding: "10px", margin: "10px" }}>
      <h3>{summary}</h3>
      <p>Severity: {severity}</p>
    </div>
  );
}