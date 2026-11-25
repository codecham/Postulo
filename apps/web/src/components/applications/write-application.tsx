import { AiGenerateForm } from "@/components/applications/ai-generate-form";
import { ClaudeCodeForm } from "@/components/applications/claude-code-form";
import { Tabs } from "@/components/ui/tabs";

type WriteApplicationProps = {
  matchId: string;
  canUseAi: boolean;
};

/** The two ways to write an application: the paid API or the free Claude Code command. */
export function WriteApplication({ matchId, canUseAi }: WriteApplicationProps) {
  return (
    <Tabs
      label="How to write the application"
      // Open the way that works: the free one when the server has no API key
      defaultId={canUseAi ? "ai" : "claude-code"}
      tabs={[
        {
          id: "ai",
          label: "Generate with AI",
          content: <AiGenerateForm matchId={matchId} isAvailable={canUseAi} />,
        },
        {
          id: "claude-code",
          label: "Claude Code (free)",
          content: <ClaudeCodeForm matchId={matchId} />,
        },
      ]}
    />
  );
}
