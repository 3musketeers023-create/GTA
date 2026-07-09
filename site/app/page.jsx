import Link from "next/link";
import { getAllPosts, formatDate } from "../lib/posts";

export default function Home() {
  const posts = getAllPosts();
  const [lead, ...rest] = posts;

  return (
    <main className="wrap">
      {lead ? (
        <section className="hero">
          <p className="kicker">Latest — updated automatically every 30 min</p>
          <h1>
            <Link href={`/post/${lead.slug}/`}>{lead.title}</Link>
          </h1>
          <p className="meta">
            {lead.excerpt} · {formatDate(lead.date)}
          </p>
        </section>
      ) : (
        <section className="hero">
          <p className="kicker">Booting up</p>
          <h1>The pipeline hasn&apos;t published yet</h1>
          <p className="meta">
            Run the GitHub Action once and articles will appear here
            automatically.
          </p>
        </section>
      )}

      <div className="ad-slot">Ad slot — AdSense unit goes here</div>

      <section className="grid">
        {rest.map((p) => (
          <Link key={p.slug} href={`/post/${p.slug}/`} className="card">
            <span className="cat">{p.category}</span>
            <h2>{p.title}</h2>
            <p>{p.excerpt}</p>
            <time dateTime={p.date}>{formatDate(p.date)}</time>
          </Link>
        ))}
      </section>
    </main>
  );
}
