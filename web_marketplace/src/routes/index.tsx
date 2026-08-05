import { createFileRoute } from "@tanstack/react-router";
import { MarketplacePage } from "@/components/marketplace-page";

export const Route = createFileRoute("/")({
  component: Home,
});

function Home() {
  return <MarketplacePage />;
}
