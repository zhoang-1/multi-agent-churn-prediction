import { useState } from 'react';
import { Search, Filter, AlertTriangle, CheckCircle, Activity, BarChart3, PieChart, BrainCircuit } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';

// Mock Data - Customers
const MOCK_CUSTOMERS = [
  { id: 'CUS-1001', name: 'Alice Smith', age: 34, tenure: 12, monthly: 55.0, contract: 'Month-to-month', churnProb: 0.85, status: 'High Risk', sentiment: 'Negative' },
  { id: 'CUS-1002', name: 'Bob Jones', age: 45, tenure: 60, monthly: 89.9, contract: 'Two year', churnProb: 0.12, status: 'Safe', sentiment: 'Positive' },
  { id: 'CUS-1003', name: 'Charlie Brown', age: 28, tenure: 2, monthly: 35.0, contract: 'Month-to-month', churnProb: 0.65, status: 'At Risk', sentiment: 'Neutral' },
  { id: 'CUS-1004', name: 'Diana Prince', age: 38, tenure: 24, monthly: 105.5, contract: 'One year', churnProb: 0.35, status: 'Safe', sentiment: 'Positive' },
  { id: 'CUS-1005', name: 'Ethan Hunt', age: 50, tenure: 48, monthly: 20.0, contract: 'Two year', churnProb: 0.05, status: 'Safe', sentiment: 'Positive' },
];

// Mock Data - Churn Model
const CHURN_MODEL_DATA = [
  { name: 'Jan', accuracy: 0.82 },
  { name: 'Feb', accuracy: 0.84 },
  { name: 'Mar', accuracy: 0.85 },
  { name: 'Apr', accuracy: 0.88 },
  { name: 'May', accuracy: 0.89 },
  { name: 'Jun', accuracy: 0.91 },
];
const CHURN_FEATURE_IMPORTANCE = [
  { name: 'Tenure', value: 45 },
  { name: 'Contract', value: 30 },
  { name: 'Monthly Charges', value: 15 },
  { name: 'Age', value: 10 },
];

// Mock Data - Sentiment Model
const SENTIMENT_MODEL_DATA = [
  { name: 'Jan', accuracy: 0.75 },
  { name: 'Feb', accuracy: 0.77 },
  { name: 'Mar', accuracy: 0.80 },
  { name: 'Apr', accuracy: 0.81 },
  { name: 'May', accuracy: 0.84 },
  { name: 'Jun', accuracy: 0.86 },
];
const SENTIMENT_KEYWORDS = [
  { name: 'Excellent', value: 40 },
  { name: 'Outage', value: 25 },
  { name: 'Expensive', value: 20 },
  { name: 'Support', value: 15 },
];

export default function Dashboard() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [activeModel, setActiveModel] = useState('churn'); // 'churn' or 'sentiment'

  const filteredCustomers = MOCK_CUSTOMERS.filter(c => 
    c.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    c.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const currentChartData = activeModel === 'churn' ? CHURN_MODEL_DATA : SENTIMENT_MODEL_DATA;
  const currentBarData = activeModel === 'churn' ? CHURN_FEATURE_IMPORTANCE : SENTIMENT_KEYWORDS;
  const chartColor = activeModel === 'churn' ? '#818cf8' : '#10b981';
  const barColor = activeModel === 'churn' ? '#22d3ee' : '#f59e0b';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Agent Dashboard</h1>
      </div>

      {/* Model Performance Section */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="glass p-6 rounded-2xl col-span-1 lg:col-span-2 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2 text-indigo-300">
              <Activity size={20} /> Model Accuracy Trend
            </h2>
            <div className="flex bg-slate-800/50 p-1 rounded-lg border border-slate-700/50">
              <button 
                onClick={() => setActiveModel('churn')}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${activeModel === 'churn' ? 'bg-indigo-500 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Churn Model
              </button>
              <button 
                onClick={() => setActiveModel('sentiment')}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${activeModel === 'sentiment' ? 'bg-emerald-500 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Sentiment Model
              </button>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={currentChartData} key={activeModel}>
                <defs>
                  <linearGradient id="colorAcc" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={chartColor} stopOpacity={0.3}/>
                    <stop offset="95%" stopColor={chartColor} stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis domain={[0.6, 1]} stroke="#94a3b8" />
                <RechartsTooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }} />
                <Area type="monotone" dataKey="accuracy" stroke={chartColor} fillOpacity={1} fill="url(#colorAcc)" strokeWidth={3} animationDuration={800} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="glass p-6 rounded-2xl shadow-lg">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 text-cyan-300">
            {activeModel === 'churn' ? <BarChart3 size={20} /> : <BrainCircuit size={20} className="text-amber-400" />} 
            {activeModel === 'churn' ? 'Feature Importance' : 'Top Keywords'}
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={currentBarData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                <XAxis type="number" stroke="#94a3b8" />
                <YAxis dataKey="name" type="category" stroke="#94a3b8" width={90} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }} />
                <Bar dataKey="value" fill={barColor} radius={[0, 4, 4, 0]} animationDuration={800} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* Customer Data Grid & Insights */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className={`glass rounded-2xl shadow-lg overflow-hidden flex flex-col ${selectedCustomer ? 'col-span-1 lg:col-span-2' : 'col-span-3'}`}>
          <div className="p-4 border-b border-slate-700/50 flex items-center justify-between bg-slate-800/30">
            <h2 className="text-lg font-semibold">Customer Base</h2>
            <div className="flex gap-3">
              <div className="relative">
                <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input 
                  type="text" 
                  placeholder="Search customers..." 
                  className="bg-slate-900 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 w-64 transition-all"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <button className="bg-slate-800 border border-slate-700 p-2 rounded-lg hover:bg-slate-700 transition-colors">
                <Filter size={18} className="text-slate-300" />
              </button>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="bg-slate-900/50 text-slate-400 uppercase text-xs">
                <tr>
                  <th className="px-6 py-4 font-semibold">ID</th>
                  <th className="px-6 py-4 font-semibold">Name</th>
                  <th className="px-6 py-4 font-semibold">Sentiment</th>
                  <th className="px-6 py-4 font-semibold">Contract</th>
                  <th className="px-6 py-4 font-semibold">Churn Risk</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filteredCustomers.map(customer => (
                  <tr 
                    key={customer.id} 
                    onClick={() => setSelectedCustomer(customer)}
                    className={`cursor-pointer transition-colors ${selectedCustomer?.id === customer.id ? 'bg-indigo-500/10' : 'hover:bg-slate-800/40'}`}
                  >
                    <td className="px-6 py-4 font-mono text-indigo-300">{customer.id}</td>
                    <td className="px-6 py-4 font-medium">{customer.name}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded text-xs border ${
                        customer.sentiment === 'Positive' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' :
                        customer.sentiment === 'Negative' ? 'bg-rose-500/10 border-rose-500/20 text-rose-400' :
                        'bg-amber-500/10 border-amber-500/20 text-amber-400'
                      }`}>
                        {customer.sentiment}
                      </span>
                    </td>
                    <td className="px-6 py-4">{customer.contract}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-full bg-slate-700 rounded-full h-2 max-w-[60px]">
                          <div 
                            className={`h-2 rounded-full ${customer.churnProb > 0.7 ? 'bg-rose-500' : customer.churnProb > 0.4 ? 'bg-amber-500' : 'bg-emerald-500'}`}
                            style={{ width: `${customer.churnProb * 100}%` }}
                          />
                        </div>
                        <span className="text-xs font-medium">{(customer.churnProb * 100).toFixed(0)}%</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Insight Panel */}
        {selectedCustomer && (
          <div className="glass rounded-2xl shadow-lg p-6 flex flex-col animate-fade-in-up border border-indigo-500/20">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold">Agent Insights</h3>
              <button onClick={() => setSelectedCustomer(null)} className="text-slate-400 hover:text-white">✕</button>
            </div>
            
            <div className="mb-6">
              <p className="text-slate-400 text-sm">Target Customer</p>
              <p className="text-2xl font-semibold text-white">{selectedCustomer.name}</p>
              <p className="font-mono text-sm text-indigo-400">{selectedCustomer.id}</p>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                <p className="text-slate-400 text-xs uppercase mb-1">Risk Status</p>
                <div className="flex items-center gap-2">
                  {selectedCustomer.churnProb > 0.7 ? <AlertTriangle size={18} className="text-rose-500" /> : <CheckCircle size={18} className="text-emerald-500" />}
                  <span className={`font-bold ${selectedCustomer.churnProb > 0.7 ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {selectedCustomer.status}
                  </span>
                </div>
              </div>
              <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                <p className="text-slate-400 text-xs uppercase mb-1">Sentiment</p>
                <span className={`font-bold ${
                        selectedCustomer.sentiment === 'Positive' ? 'text-emerald-400' :
                        selectedCustomer.sentiment === 'Negative' ? 'text-rose-400' : 'text-amber-400'
                      }`}>
                  {selectedCustomer.sentiment}
                </span>
              </div>
            </div>

            <div className="space-y-4 flex-1">
              <div>
                <h4 className="text-sm font-semibold text-cyan-300 mb-2 flex items-center gap-2">
                  <PieChart size={16} /> Analysis Report
                </h4>
                <p className="text-sm text-slate-300 leading-relaxed bg-slate-900/30 p-3 rounded-lg border border-slate-800">
                  {selectedCustomer.churnProb > 0.7 
                    ? `This customer has a high likelihood of churning due to a short tenure (${selectedCustomer.tenure} mos) combined with a ${selectedCustomer.contract} contract. Sentiment analysis detected '${selectedCustomer.sentiment}' feedback indicating frustration.` 
                    : `Customer exhibits strong loyalty indicators with a ${selectedCustomer.tenure} month history. The recent '${selectedCustomer.sentiment}' sentiment confirms they are satisfied.`}
                </p>
              </div>
              
              <div>
                <h4 className="text-sm font-semibold text-emerald-400 mb-2">Recommended Action</h4>
                <div className="bg-emerald-500/10 border border-emerald-500/20 p-3 rounded-lg">
                  <p className="text-sm text-emerald-200">
                    {selectedCustomer.churnProb > 0.7 
                      ? "Offer a 20% discount to upgrade to a 'One year' contract and proactively address their negative feedback." 
                      : "Send a 'Thank You' loyalty reward and soft-upsell premium services."}
                  </p>
                </div>
              </div>
            </div>
            
            <button className="w-full mt-6 bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2.5 rounded-lg transition-colors">
              Execute Action
            </button>
          </div>
        )}
      </section>
    </div>
  );
}
