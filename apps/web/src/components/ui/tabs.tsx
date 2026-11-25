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
};

/** Show one panel at a time. Hidden panels stay mounted, so they keep their input. */
export function Tabs({ label, tabs }: TabsProps) {
  const [activeId, setActiveId] = useState(tabs[0]?.id);

  return (
    <div className="flex flex-col gap-6">
      <div
        role="tablist"
        aria-label={label}
        className="flex gap-1 border-b border-gray-200 dark:border-gray-800"
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
              className={`-mb-px border-b-2 px-4 py-2 text-sm font-medium ${
                isActive
                  ? "border-gray-900 dark:border-white"
                  : "border-transparent text-gray-500 hover:text-gray-900 dark:hover:text-white"
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
