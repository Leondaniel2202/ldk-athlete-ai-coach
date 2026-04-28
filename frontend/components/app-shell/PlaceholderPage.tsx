interface PlaceholderPageProps {
  eyebrow: string;
  title: string;
  description: string;
  items: string[];
}

export function PlaceholderPage({ eyebrow, title, description, items }: PlaceholderPageProps) {
  return (
    <section className="max-w-3xl">
      <p className="text-sm font-semibold text-emerald-700">{eyebrow}</p>
      <h2 className="mt-2 text-3xl font-semibold tracking-tight text-zinc-950">{title}</h2>
      <p className="mt-3 text-base leading-7 text-zinc-600">{description}</p>

      <div className="mt-8 rounded-lg border border-zinc-200 bg-white p-5 shadow-sm">
        <h3 className="text-base font-semibold text-zinc-950">Planned capabilities</h3>
        <ul className="mt-4 grid gap-3 sm:grid-cols-2">
          {items.map((item) => (
            <li
              key={item}
              className="rounded-lg border border-zinc-200 bg-stone-50 px-4 py-3 text-sm font-medium text-zinc-700"
            >
              {item}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
