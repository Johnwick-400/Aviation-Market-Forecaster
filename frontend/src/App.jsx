import React, { useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Area, ComposedChart, ResponsiveContainer } from 'recharts';
import { PlaneTakeoff, Search, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

export default function App() {
  const [origin, setOrigin] = useState('');
  const [dest, setDest] = useState('');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const fetchForecast = async (e) => {
    e.preventDefault();
    if (!origin || !dest) return;

    setLoading(true);
    setError(null);
    setData(null);

    try {
      const res = await axios.get(`http://localhost:8000/forecast/${origin}/${dest}`);
      const formattedData = res.data.forecast.map(d => ({
        date: d.date,
        predicted: d.predicted_passengers,
        confidence_band: [d.p10, d.p90]
      }));
      setData({ route: res.data.route, chartData: formattedData });
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to fetch forecast. Ensure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8 font-sans overflow-hidden">
      {/* Animated Header */}
      <motion.header 
        initial={{ opacity: 0, y: -30 }} 
        animate={{ opacity: 1, y: 0 }} 
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="mb-10 flex items-center gap-4 border-b border-slate-800 pb-6"
      >
        <div className="bg-emerald-500/10 p-4 rounded-xl border border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
          <PlaneTakeoff className="text-emerald-400" size={40} />
        </div>
        <div>
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
            Aviation Market Forecaster
          </h1>
          <p className="text-slate-400 mt-1 font-medium tracking-wide">Powered by Google TimesFM Zero-Shot Prediction</p>
        </div>
      </motion.header>

      <main className="max-w-6xl mx-auto space-y-8">
        
        {/* Animated Search Bar */}
        <motion.section 
          initial={{ opacity: 0, scale: 0.95 }} 
          animate={{ opacity: 1, scale: 1 }} 
          transition={{ delay: 0.2, duration: 0.5 }}
          className="bg-slate-800/50 backdrop-blur-sm p-8 rounded-2xl border border-slate-700 shadow-2xl relative overflow-hidden"
        >
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-500 to-cyan-500 opacity-50"></div>
          <form onSubmit={fetchForecast} className="flex flex-col md:flex-row gap-6 items-end">
            <div className="flex-1 w-full">
              <label className="block text-sm font-semibold text-slate-300 mb-2 uppercase tracking-wider">Origin IATA</label>
              <input 
                type="text" 
                value={origin}
                onChange={(e) => setOrigin(e.target.value.toUpperCase())}
                className="w-full bg-slate-900/80 border border-slate-600 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 rounded-xl px-4 py-3 text-white uppercase transition-all shadow-inner"
                maxLength={3}
                placeholder="e.g. JFK"
              />
            </div>
            <div className="flex-1 w-full">
              <label className="block text-sm font-semibold text-slate-300 mb-2 uppercase tracking-wider">Destination IATA</label>
              <input 
                type="text" 
                value={dest}
                onChange={(e) => setDest(e.target.value.toUpperCase())}
                className="w-full bg-slate-900/80 border border-slate-600 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 rounded-xl px-4 py-3 text-white uppercase transition-all shadow-inner"
                maxLength={3}
                placeholder="e.g. LHR"
              />
            </div>
            <motion.button 
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading || !origin || !dest}
              className="bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 disabled:from-slate-700 disabled:to-slate-600 px-8 py-3 rounded-xl font-bold flex items-center gap-3 transition-all shadow-[0_0_20px_rgba(16,185,129,0.3)] disabled:shadow-none w-full md:w-auto justify-center"
            >
              {loading ? <Activity className="animate-spin" /> : <Search size={20} />}
              {loading ? 'Forecasting...' : 'Generate Forecast'}
            </motion.button>
          </form>
        </motion.section>

        {/* Error Display */}
        {error && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            className="bg-red-900/40 border border-red-500/50 text-red-200 p-4 rounded-xl backdrop-blur-sm"
          >
            {error}
          </motion.div>
        )}

        {/* Chart Display */}
        {data && (
          <motion.section 
            initial={{ opacity: 0, y: 30 }} 
            animate={{ opacity: 1, y: 0 }} 
            transition={{ duration: 0.7, type: "spring", bounce: 0.4 }}
            className="bg-slate-800/50 backdrop-blur-md p-8 rounded-2xl border border-slate-700 shadow-2xl h-[550px] relative"
          >
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                Route Demand Forecast: {data.route}
              </h2>
              <span className="bg-emerald-500/20 text-emerald-300 px-4 py-1.5 rounded-full text-sm font-bold border border-emerald-500/30">
                24-Month Horizon
              </span>
            </div>
            
            <ResponsiveContainer width="100%" height="90%">
              <ComposedChart data={data.chartData} margin={{ top: 10, right: 30, left: 20, bottom: 30 }}>
                <defs>
                  <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="date" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} dy={10} />
                <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} dx={-10} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.9)', border: '1px solid #475569', borderRadius: '12px', backdropFilter: 'blur(4px)' }}
                  itemStyle={{ color: '#fff' }}
                  cursor={{ stroke: '#10b981', strokeWidth: 1, strokeDasharray: '5 5' }}
                />
                <Legend wrapperStyle={{ paddingTop: '20px' }}/>
                <Area 
                  type="monotone" 
                  dataKey="confidence_band" 
                  stroke="none" 
                  fill="#0ea5e9" 
                  fillOpacity={0.15} 
                  name="P10-P90 Confidence Interval" 
                />
                <Area 
                  type="monotone" 
                  dataKey="predicted" 
                  stroke="none" 
                  fill="url(#colorPredicted)" 
                />
                <Line 
                  type="monotone" 
                  dataKey="predicted" 
                  stroke="#10b981" 
                  strokeWidth={4} 
                  name="Median Forecast (P50)" 
                  dot={{ r: 4, strokeWidth: 2, fill: '#1e293b' }} 
                  activeDot={{ r: 8, stroke: '#10b981', strokeWidth: 2, fill: '#fff' }} 
                  animationDuration={2000}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </motion.section>
        )}
      </main>
    </div>
  );
}