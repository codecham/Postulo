"use client";

import { type ReactNode, useState } from "react";

export type Tab = {
  id: string;
  label: string;
  content: ReactNode; // can be rendered on the server
};

type TabsProps = {
  label: string; // what the tabs choose between, for screen readers
  tabs: Tab[];
  defaultId?: string; // the tab shown first (the first one by default)
};

/** Show one panel at a time. Hidden panels stay mounted, so they keep their input. */
export function Tabs({ label, tabs, defaultId }: TabsProps) {
  const [activeId, setActiveId] = useState(defaultId ?? tabs[0]?.id);

  return (
    <div className="flex flex-col gap-6">
      <div
        role="tablist"
        aria-label={label}
        className="bg-subtle flex w-fit max-w-full gap-1 overflow-x-auto rounded-lg p-1"
      >
        {tabs.map((tab) => {
          const isActive = tab.id === activeId;
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              id={`tab-${tab.id}`}
              aria-selected={isActive}
              aria-controls={`panel-${tab.id}`}
              onClick={() => setActiveId(tab.id)}
              className={`rounded-md px-3 py-1.5 text-sm font-medium whitespace-nowrap transition-colors ${
                isActive
                  ? "bg-surface text-fg shadow-sm"
                  : "text-muted hover:text-fg"
              }`}
            >
              {tab.label}
            </button>
          );
        })}
      </div>
      {tabs.map((tab) => (
        <div
          key={tab.id}
          role="tabpanel"
          id={`panel-${tab.id}`}
          aria-labelledby={`tab-${tab.id}`}
          hidden={tab.id !== activeId}
        >
          {tab.content}
        </div>
      ))}
    </div>
  );
}
