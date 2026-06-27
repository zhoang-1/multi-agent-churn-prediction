import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, Activity, BarChart3, BrainCircuit, User } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { customerApi } from '../services/api';

// Mock Data - initial list
const MOCK_CUSTOMERS = [
  { id: 'CUS-1001', name: 'Alice Smith', age: 34, tenure: 12, monthly: 55.0, contract: 'Month-to-month', churnProb: 0.85, sentiment: 'Negative', phone: '0901234567', email: 'alice@example.com' },
  { id: 'CUS-1002', name: 'Bob Jones', age: 45, tenure: 60, monthly: 89.9, contract: 'Two year', churnProb: 0.12, sentiment: 'Positive', phone: '0912345678', email: 'bob@example.com' },
];

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
  const [customers, setCustomers] = useState(MOCK_CUSTOMERS);
  const [loading, setLoading] = useState(false);
  const [activeModel, setActiveModel] = useState('churn'); 
  const navigate = useNavigate();

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      setCustomers(MOCK_CUSTOMERS);
      return;
    }
    setLoading(true);
    try {
      // Determine what the search term is
      let query = {};
      if (searchTerm.includes('@')) {
        query = { email: searchTerm };
      } else if (/^\d+$/.test(searchTerm)) {
        query = { phone: searchTerm };
      } else {
        query = { customer_id: searchTerm };
      }
      
      const res = await customerApi.getData(query);
      
      if (res && res.data) {
        // Map backend order format to list format
        const customerData = Array.isArray(res.data) ? res.data[0] : res.data;
        if (customerData && customerData.customer_profile) {
          const profile = customerData.customer_profile;
          setCustomers([{
             id: profile.customer_id || searchTerm,
             name: profile.full_name || 'Unknown',
             sentiment: 'Unknown', // Will be fetched in detail page
             contract: 'Unknown',
             churnProb: 0.5, // Will be fetched in detail page
             phone: profile.phone,
             email: profile.email
          }]);
        } else {
          setCustomers([]);
        }
      } else {
        setCustomers([]);
      }
    } catch (error) {
      console.error('Search failed:', error);
      // fallback to mock filter for demo
      const filtered = MOCK_CUSTOMERS.filter(c => 
        c.phone?.includes(searchTerm) || 
        c.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.id?.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setCustomers(filtered);
    } finally {
      setLoading(false);
    }
  };

  const currentChartData = activeModel === 'churn' ? CHURN_MODEL_DATA : SENTIMENT_MODEL_DATA;
  const currentBarData = activeModel === 'churn' ? CHURN_FEATURE_IMPORTANCE : SENTIMENT_KEYWORDS;
  const chartColor = activeModel === 'churn' ? '#4f46e5' : '#059669';
  const barColor = activeModel === 'churn' ? '#0ea5e9' : '#d97706';

  return (
    <div className="space-y-6 text-slate-800">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-slate-900">Agent Dashboard</h1>
      </div>

      {/* Model Performance Section */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="glass p-6 rounded-2xl col-span-1 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2 text-indigo-700">
              <Activity size={20} /> Model Accuracy Trend
            </h2>
            <div className="flex bg-slate-100 p-1 rounded-lg border border-slate-200">
              <button 
                onClick={() => setActiveModel('churn')}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${activeModel === 'churn' ? 'bg-indigo-600 text-white shadow' : 'text-slate-600 hover:text-slate-900'}`}
              >
                Churn Model
              </button>
              <button 
                onClick={() => setActiveModel('sentiment')}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${activeModel === 'sentiment' ? 'bg-emerald-600 text-white shadow' : 'text-slate-600 hover:text-slate-900'}`}
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
                    <stop offset="5%" stopColor={chartColor} stopOpacity={0.2}/>
                    <stop offset="95%" stopColor={chartColor} stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" stroke="#64748b" />
                <YAxis domain={[0.6, 1]} stroke="#64748b" />
                <RechartsTooltip contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', color: '#1e293b' }} />
                <Area type="monotone" dataKey="accuracy" stroke={chartColor} fillOpacity={1} fill="url(#colorAcc)" strokeWidth={3} animationDuration={800} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="glass p-6 rounded-2xl">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 text-cyan-700">
            {activeModel === 'churn' ? <BarChart3 size={20} /> : <BrainCircuit size={20} className="text-amber-600" />} 
            {activeModel === 'churn' ? 'Feature Importance' : 'Top Keywords'}
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={currentBarData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
                <XAxis type="number" stroke="#64748b" />
                <YAxis dataKey="name" type="category" stroke="#64748b" width={90} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', color: '#1e293b' }} />
                <Bar dataKey="value" fill={barColor} radius={[0, 4, 4, 0]} animationDuration={800} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* Customer Data Grid */}
      <section className="glass rounded-2xl overflow-hidden flex flex-col">
        <div className="p-5 border-b border-slate-200 flex items-center justify-between bg-slate-50/80">
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            <User className="text-indigo-600" /> Customer Base
          </h2>
          <div className="flex gap-3">
            <div className="relative flex">
              <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input 
                type="text" 
                placeholder="Search ID, phone or email..." 
                className="bg-white border border-slate-300 rounded-l-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 w-64 transition-all text-slate-700"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
              <button 
                onClick={handleSearch}
                className="bg-indigo-600 text-white px-4 py-2 rounded-r-lg hover:bg-indigo-700 transition-colors text-sm font-medium"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
            <button className="bg-white border border-slate-300 p-2 rounded-lg hover:bg-slate-50 transition-colors shadow-sm">
              <Filter size={18} className="text-slate-500" />
            </button>
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-slate-100 text-slate-600 uppercase text-xs font-bold">
              <tr>
                <th className="px-6 py-4">ID</th>
                <th className="px-6 py-4">Name</th>
                <th className="px-6 py-4">Contact</th>
                <th className="px-6 py-4">Sentiment</th>
                <th className="px-6 py-4">Contract</th>
                <th className="px-6 py-4">Churn Risk</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white/50">
              {customers.length > 0 ? customers.map(customer => (
                <tr 
                  key={customer.id} 
                  onClick={() => navigate(`/customer/${customer.id}`)}
                  className="cursor-pointer transition-colors hover:bg-indigo-50/60 group"
                >
                  <td className="px-6 py-4 font-mono text-indigo-600 font-medium">{customer.id}</td>
                  <td className="px-6 py-4 font-medium text-slate-800">{customer.name}</td>
                  <td className="px-6 py-4 text-slate-500 text-xs">
                     <div>{customer.email}</div>
                     <div>{customer.phone}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${
                      customer.sentiment === 'Positive' ? 'bg-emerald-100 border-emerald-200 text-emerald-700' :
                      customer.sentiment === 'Negative' ? 'bg-rose-100 border-rose-200 text-rose-700' :
                      'bg-amber-100 border-amber-200 text-amber-700'
                    }`}>
                      {customer.sentiment}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-600">{customer.contract}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-full bg-slate-200 rounded-full h-2.5 max-w-[80px] overflow-hidden">
                        <div 
                          className={`h-2.5 rounded-full ${customer.churnProb > 0.7 ? 'bg-rose-500' : customer.churnProb > 0.4 ? 'bg-amber-500' : 'bg-emerald-500'}`}
                          style={{ width: `${customer.churnProb * 100}%` }}
                        />
                      </div>
                      <span className="text-xs font-semibold text-slate-700">{(customer.churnProb * 100).toFixed(0)}%</span>
                    </div>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-slate-500">
                    No customers found. Try searching a valid ID, phone, or email.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
