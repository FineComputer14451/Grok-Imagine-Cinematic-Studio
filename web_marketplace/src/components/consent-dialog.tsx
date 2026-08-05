import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useMarketplace } from "@/store/marketplace";
import { toast } from "sonner";

type Props = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConsented?: () => void;
};

export function ConsentDialog({ open, onOpenChange, onConsented }: Props) {
  const grant = useMarketplace((s) => s.grantNsfwConsent);
  const install = useMarketplace((s) => s.install);

  const handleConsent = () => {
    grant();
    const res = install("grok-imagine-nsfw");
    onOpenChange(false);
    if (res.ok) {
      toast.success(res.message);
      onConsented?.();
    } else toast.error(res.message);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>NSFW pack requires consent</DialogTitle>
          <DialogDescription>
            The NSFW pack includes ErosForge director tools and adult-oriented
            sequence / quota / chain QA skills. It is an explicit opt-in and is
            not installed by default with modular satellite packs (full suite
            includes it). Confirm you are 18+ and want these tools available.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="secondary" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleConsent}>I consent — install pack</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
