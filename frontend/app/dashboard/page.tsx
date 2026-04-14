"use client"

import { useEffect, useState, Suspense, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';

const API_BASE = 'http://localhost:8000';

interface ArtistStats {
  artistName: string;
  noStreams: number;
  streamTimeHr: number;
}

interface TrackStats {
  artistName: string;
  trackName: string;
  noStreams: number;
  streamTimeHr: number;
  fullName?: string;
}

interface WeekdayStats {
  weekday: string;
  hrPlayedAvg: number;
  noStreamsAvg: number;
  lenStreamsAvgMin: number;
}

interface ListeningDay {
  date: string;
  hours: number;
}

interface AnalysisResult {
  listening_over_time: ListeningDay[];
  top_artists: ArtistStats[];
  top_tracks: TrackStats[];
  weekday_stats: WeekdayStats[];
  total_hours: number;
  total_streams: number;
}

type TimeRange = 'short_term' | 'medium_term' | 'long_term';

const TIME_RANGE_LABELS: Record<TimeRange, string> = {
  short_term: 'Last 4 Weeks',
  medium_term: 'Last 6 Months',
  long_term: 'All Time',
};

export default function Dashboard() {
  return (
    <Suspense fallback={<LoadingScreen />}>
      <DashboardContent />
    </Suspense>
  );
}

function LoadingScreen() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-green-900 to-black text-white flex items-center justify-center">
      <p className="text-gray-400 text-lg animate-pulse">Loading…</p>
    </div>
  );
}

function DashboardContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const sessionId = searchParams.get('session_id');

  const [analysisData, setAnalysisData] = useState<AnalysisResult | null>(null);
  const [timeRange, setTimeRange] = useState<TimeRange>('medium_term');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'artists' | 'tracks' | 'weekdays' | 'timeline'>('artists');

  const fetchData = useCallback(async () => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const [artistsRes, tracksRes] = await Promise.all([
        fetch(`${API_BASE}/api/top-artists?session_id=${sessionId}&time_range=${timeRange}`),
        fetch(`${API_BASE}/api/top-tracks?session_id=${sessionId}&time_range=${timeRange}`),
      ]);

      if (!artistsRes.ok || !tracksRes.ok) {
        const failedRes = !artistsRes.ok ? artistsRes : tracksRes;
        throw new Error(`API request failed with status ${failedRes.status}. Make sure the backend is running and your session is valid.`);
      }

      const artistsData = await artistsRes.json();
      const tracksData = await tracksRes.json();

      // Build a mock AnalysisResult from the two endpoints
      setAnalysisData({
        listening_over_time: [],
        top_artists: artistsData.artists ?? [],
        top_tracks: tracksData.tracks ?? [],
        weekday_stats: [],
        total_hours: 0,
        total_streams: 0,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  }, [sessionId, timeRange]);

  useEffect(() => {
    if (!sessionId) {
      router.push('/');
      return;
    }
    fetchData();
  }, [sessionId, timeRange, fetchData, router]);

  if (!sessionId) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-900 to-black text-white">
      <header className="border-b border-white/10 px-6 py-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold">🎵 Spotify Activity Analyzer</h1>
        <button
          onClick={() => router.push('/')}
          className="text-sm text-gray-400 hover:text-white transition"
        >
          ← Back
        </button>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Time range selector */}
        <div className="flex gap-2 mb-8">
          {(Object.keys(TIME_RANGE_LABELS) as TimeRange[]).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 rounded-full text-sm font-semibold transition ${
                timeRange === range
                  ? 'bg-green-500 text-black'
                  : 'bg-white/10 hover:bg-white/20 text-white'
              }`}
            >
              {TIME_RANGE_LABELS[range]}
            </button>
          ))}
        </div>

        {loading && (
          <div className="flex justify-center items-center h-64">
            <div className="text-gray-400 text-lg animate-pulse">Loading your stats…</div>
          </div>
        )}

        {error && (
          <div className="bg-red-900/50 border border-red-500 text-red-200 rounded-xl p-6 mb-6">
            <p className="font-semibold mb-1">Error</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {!loading && !error && analysisData && (
          <>
            {/* Summary cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <StatCard label="Top Artists" value={analysisData.top_artists.length.toString()} />
              <StatCard label="Top Tracks" value={analysisData.top_tracks.length.toString()} />
              <StatCard label="Total Hours" value={analysisData.total_hours > 0 ? analysisData.total_hours.toFixed(1) : '—'} />
              <StatCard label="Total Streams" value={analysisData.total_streams > 0 ? analysisData.total_streams.toString() : '—'} />
            </div>

            {/* Tab nav */}
            <div className="flex gap-2 mb-6 border-b border-white/10">
              {(['artists', 'tracks', 'weekdays', 'timeline'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`pb-2 px-1 text-sm font-medium capitalize transition border-b-2 ${
                    activeTab === tab
                      ? 'border-green-500 text-white'
                      : 'border-transparent text-gray-400 hover:text-white'
                  }`}
                >
                  {tab === 'weekdays' ? 'By Weekday' : tab === 'timeline' ? 'Timeline' : `Top ${tab.charAt(0).toUpperCase() + tab.slice(1)}`}
                </button>
              ))}
            </div>

            {/* Tab content */}
            {activeTab === 'artists' && (
              <div>
                <h2 className="text-xl font-bold mb-4">Top Artists</h2>
                {analysisData.top_artists.length > 0 ? (
                  <ResponsiveContainer width="100%" height={350}>
                    <BarChart data={analysisData.top_artists.slice(0, 10)} layout="vertical" margin={{ left: 120 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                      <XAxis type="number" stroke="#9ca3af" />
                      <YAxis type="category" dataKey="artistName" stroke="#9ca3af" width={120} tick={{ fontSize: 12 }} />
                      <Tooltip contentStyle={{ background: '#1a1a1a', border: '1px solid #ffffff30' }} />
                      <Bar dataKey="noStreams" name="Streams" fill="#22c55e" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <EmptyState message="No artist data available for this time range." />
                )}
              </div>
            )}

            {activeTab === 'tracks' && (
              <div>
                <h2 className="text-xl font-bold mb-4">Top Tracks</h2>
                {analysisData.top_tracks.length > 0 ? (
                  <ResponsiveContainer width="100%" height={350}>
                    <BarChart
                      data={analysisData.top_tracks.slice(0, 10).map((t) => ({
                        ...t,
                        label: t.fullName ?? `${t.trackName} – ${t.artistName}`,
                      }))}
                      layout="vertical"
                      margin={{ left: 180 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                      <XAxis type="number" stroke="#9ca3af" />
                      <YAxis type="category" dataKey="label" stroke="#9ca3af" width={180} tick={{ fontSize: 11 }} />
                      <Tooltip contentStyle={{ background: '#1a1a1a', border: '1px solid #ffffff30' }} />
                      <Bar dataKey="noStreams" name="Streams" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <EmptyState message="No track data available for this time range." />
                )}
              </div>
            )}

            {activeTab === 'weekdays' && (
              <div>
                <h2 className="text-xl font-bold mb-4">Listening by Weekday</h2>
                {analysisData.weekday_stats.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={analysisData.weekday_stats}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                      <XAxis dataKey="weekday" stroke="#9ca3af" />
                      <YAxis stroke="#9ca3af" />
                      <Tooltip contentStyle={{ background: '#1a1a1a', border: '1px solid #ffffff30' }} />
                      <Bar dataKey="hrPlayedAvg" name="Avg Hours" fill="#a855f7" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <EmptyState message="Weekday stats are available when you upload your Spotify Extended History JSON files." />
                )}
              </div>
            )}

            {activeTab === 'timeline' && (
              <div>
                <h2 className="text-xl font-bold mb-4">Listening Over Time</h2>
                {analysisData.listening_over_time.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={analysisData.listening_over_time}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                      <XAxis dataKey="date" stroke="#9ca3af" tick={{ fontSize: 11 }} />
                      <YAxis stroke="#9ca3af" />
                      <Tooltip contentStyle={{ background: '#1a1a1a', border: '1px solid #ffffff30' }} />
                      <Line type="monotone" dataKey="hours" name="Hours" stroke="#22c55e" dot={false} strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <EmptyState message="Timeline data is available when you upload your Spotify Extended History JSON files." />
                )}
              </div>
            )}
          </>
        )}

        {!loading && !error && !analysisData && (
          <div className="flex justify-center items-center h-64">
            <p className="text-gray-400">Connect your Spotify account to see your stats.</p>
          </div>
        )}
      </main>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white/10 backdrop-blur rounded-xl p-4 text-center">
      <p className="text-3xl font-bold text-green-400">{value}</p>
      <p className="text-sm text-gray-300 mt-1">{label}</p>
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex items-center justify-center h-48 rounded-xl bg-white/5 border border-white/10">
      <p className="text-gray-400 text-sm text-center px-8">{message}</p>
    </div>
  );
}
