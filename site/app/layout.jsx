import "./globals.css";
import Link from "next/link";

const SITE_NAME = "Vice Wire"; // rename to whatever domain you buy

export const metadata = {
  title: {
    default: `${SITE_NAME} — GTA 6 News, Leaks & Release Updates`,
    template: `%s — ${SITE_NAME}`,
  },
  description:
    "Automated, always-current GTA 6 coverage: official Rockstar news, trailers, credible leaks and community highlights — updated every 30 minutes.",
  metadataBase: new URL(process.env.SITE_URL || "https://example.com"),
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        {/* AdSense: uncomment after approval and paste your client ID
        <script
          async
          src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX"
          crossOrigin="anonymous"
        /> */}
      </head>
      <body>
        <header className="site">
          <div className="wrap masthead">
            <Link href="/" className="logo">
              Vice<em>Wire</em>
            </Link>
            <nav className="site">
              <Link href="/">Latest</Link>
              <Link href="/about/">About</Link>
              <Link href="/privacy/">Privacy</Link>
            </nav>
          </div>
        </header>
        {children}
        <footer className="site">
          <div className="wrap">
            <div>
              <Link href="/about/">About</Link>
              <Link href="/privacy/">Privacy Policy</Link>
            </div>
            <p className="disclaimer">
              {SITE_NAME} is an independent fan-run news site. We are not
              affiliated with, endorsed by, or connected to Rockstar Games or
              Take-Two Interactive. Grand Theft Auto and GTA are trademarks of
              Take-Two Interactive. All articles are original writing with
              linked attribution to primary sources.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
