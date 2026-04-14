"use client"

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-green-900 to-black text-white">
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-6xl font-bold mb-4">Spotify Activity Analyzer</h1>
        <p className="text-2xl mb-8 text-gray-300">
          Discover your listening habits. Share your story.
        </p>
        
        <button 
          onClick={handleLogin}
          className="bg-green-500 hover:bg-green-600 text-black font-bold py-4 px-8 rounded-full text-lg transition"
        >
          Connect with Spotify
        </button>
        
        <div className="mt-16 grid md:grid-cols-3 gap-8">
          <FeatureCard 
            icon="📊"
            title="Analyze Your Stats"
            description="See your top artists, tracks, and listening patterns"
          />
          <FeatureCard 
            icon="📅"
            title="Choose Any Date Range"
            description="Not just year-end - analyze any period you want"
          />
          <FeatureCard 
            icon="📱"
            title="Share on Social"
            description="Create beautiful cards to share on Instagram, Twitter"
          />
        </div>
      </div>
    </main>
  );

  function handleLogin() {
    window.location.href = 'http://localhost:8000/auth/login';
  }
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="bg-white/10 backdrop-blur rounded-xl p-6">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-gray-300">{description}</p>
    </div>
  );
}