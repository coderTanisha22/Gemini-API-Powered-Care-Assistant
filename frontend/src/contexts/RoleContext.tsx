import React, { createContext, useContext, useState } from "react";

export type UserRole = "caregiver" | "supervisor" | "family";

interface RoleContextType {
  role: UserRole;
  setRole: (role: UserRole) => void;
  userName: string;
}

const RoleContext = createContext<RoleContextType>({
  role: "caregiver",
  setRole: () => {},
  userName: "Sarah Johnson",
});

export const RoleProvider = ({ children }: { children: React.ReactNode }) => {
  const [role, setRole] = useState<UserRole>("caregiver");
  return (
    <RoleContext.Provider value={{ role, setRole, userName: "Sarah Johnson" }}>
      {children}
    </RoleContext.Provider>
  );
};

export const useRole = () => useContext(RoleContext);
