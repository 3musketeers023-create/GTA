import { getAllPosts, getPost, formatDate } from "../../../lib/posts";

export function generateStaticParams() {
  return getAllPosts().map((p) => ({ slug: p.slug }));
}

export function generateMetadata({ params }) {
  const post = getPost(params.slug);
  if (!post) return {};
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: { title: post.title, description: post.excerpt, type: "article" },
  };
}

export default function PostPage({ params }) {
  const post = getPost(params.slug);
  if (!post) return <main className="wrap page-prose"><h1>Not found</h1></main>;

  return (
    <main className="wrap">
      <article className="post">
        <span className="cat">{post.category}</span>
        <h1>{post.title}</h1>
        <p className="byline">
          {formatDate(post.date)} · {post.tags.join(" · ")}
        </p>

        <div className="ad-slot">Ad slot — in-article unit</div>

        <div className="body" dangerouslySetInnerHTML={{ __html: post.html }} />

        {post.sourceUrl && (
          <div className="source-box">
            Originally reported by{" "}
            <a href={post.sourceUrl} rel="noopener nofollow" target="_blank">
              {post.sourceName || "source"}
            </a>
            . This article is an original summary written for Vice Wire.
          </div>
        )}

        <div className="ad-slot">Ad slot — below article</div>
      </article>
    </main>
  );
}
