import { Bell, LogOut, Heart } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useRole, UserRole } from "@/contexts/RoleContext";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { toast } from "sonner";

export function Navbar() {
  const { role, setRole, userName } = useRole();

  const handleNotification = () => {
    toast("Unusual inactivity detected. Review recommended.", {
      description: "2 minutes ago",
      duration: 5000,
    });
  };

  return (
    <header className="h-14 border-b border-border bg-card flex items-center justify-between px-4 shadow-card">
      <div className="flex items-center gap-2">
        <SidebarTrigger className="text-muted-foreground hover:text-foreground" />
        <div className="flex items-center gap-2 ml-2">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <Heart className="w-4 h-4 text-primary-foreground" />
          </div>
          <span className="font-heading font-semibold text-foreground text-lg hidden sm:inline">
            Care Assistant
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden sm:flex items-center gap-2">
          <span className="text-sm text-muted-foreground">{userName}</span>
          <Select value={role} onValueChange={(v) => setRole(v as UserRole)}>
            <SelectTrigger className="w-32 h-8 text-xs bg-secondary border-0">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="caregiver">Caregiver</SelectItem>
              <SelectItem value="supervisor">Supervisor</SelectItem>
              <SelectItem value="family">Family</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <Button variant="ghost" size="icon" onClick={handleNotification} className="relative text-muted-foreground hover:text-foreground">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-calm-alert rounded-full" />
        </Button>

        <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
          <LogOut className="w-5 h-5" />
        </Button>
      </div>
    </header>
  );
}
