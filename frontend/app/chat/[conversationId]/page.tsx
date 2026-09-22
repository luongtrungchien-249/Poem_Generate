import { AppShell } from "@/components/AppShell";

export default async function TrangChat({
  params,
}: {
  params: Promise<{ conversationId: string }>;
}) {
  const { conversationId } = await params;
  return <AppShell conversationId={conversationId} />;
}
