/** The offer's text, as plain text from the job board, with its line breaks. */
export function OfferDescription({ description }: { description: string }) {
  return (
    <div className="text-sm leading-relaxed whitespace-pre-line">
      {description}
    </div>
  );
}
