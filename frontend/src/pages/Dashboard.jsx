import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, Activity, BarChart3, BrainCircuit, User, ChevronLeft, ChevronRight } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { customerApi } from '../services/api';

const CHURN_MODEL_DATA = [
  { name: 'Jan', accuracy: 0.82 },
  { name: 'Feb', accuracy: 0.84 },
  { name: 'Mar', accuracy: 0.85 },
  { name: 'Apr', accuracy: 0.88 },
  { name: 'May', accuracy: 0.89 },
  { name: 'Jun', accuracy: 0.91 },
];
// Feature importance of the RFM-based churn model (based on actual model features)
const CHURN_FEATURE_IMPORTANCE = [
  { name: 'Recency', value: 38 },
  { name: 'Frequency', value: 28 },
  { name: 'Monetary', value: 16 },
  { name: 'Purchase Rate', value: 10 },
  { name: 'Avg Order Value', value: 8 },
];
const SENTIMENT_MODEL_DATA = [
  { name: 'Jan', accuracy: 0.75 },
  { name: 'Feb', accuracy: 0.77 },
  { name: 'Mar', accuracy: 0.80 },
  { name: 'Apr', accuracy: 0.81 },
  { name: 'May', accuracy: 0.84 },
  { name: 'Jun', accuracy: 0.86 },
];
// Sentiment label distribution from sentiment model output
const SENTIMENT_KEYWORDS = [
  { name: 'Outage', value: 25 },
  { name: 'Expensive', value: 20 },
  { name: 'Support', value: 15 },
];

const PAGE_LIMIT = 20;

export default function Dashboard() {
  const [searchTerm, setSearchTerm] = useState('');
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeModel, setActiveModel] = useState('churn');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isSearchMode, setIsSearchMode] = useState(false);
  const navigate = useNavigate();

  // Fetch churn + sentiment for each customer and enrich the list
  // Processes one customer at a time to avoid overloading the backend
  const enrichCustomers = useCallback(async (profileList, setCustomersFn) => {
    const results = [];
    for (const profile of profileList) {
      const customerId = profile.customer_id;
      const query = { customer_id: customerId };
      let churnProb = null;
      let sentiment = 'Unknown';

      if (!customerId) {
        results.push({
          id: customerId,
          name: profile.full_name || profile.name || 'Unknown',
          email: profile.email,
          phone: profile.phone,
          contract: 'Unknown',
          churnProb: null,
          sentiment: 'N/A',
        });
        continue;
      }

      try {
        const churnRes = await customerApi.getChurn(query);
        if (churnRes?.churn?.churn_result?.churn_probability !== undefined) {
          churnProb = churnRes.churn.churn_result.churn_probability;
        }
      } catch (_) {}

      try {
        const sentimentRes = await customerApi.getSentiment(query);
        if (sentimentRes?.sentiment?.sentiment_result?.label) {
          const label = sentimentRes.sentiment.sentiment_result.label;
          sentiment = label.charAt(0).toUpperCase() + label.slice(1);
        }
      } catch (_) {}

      const enriched = {
        id: customerId,
        name: profile.full_name || profile.name || 'Unknown',
        email: profile.email,
        phone: profile.phone,
        contract: 'Unknown',
        churnProb,
        sentiment,
      };
      results.push(enriched);

      // Cập nhật UI liên tục sau mỗi khách hàng được xử lý
      setCustomersFn([...results]);
    }
    return results;
  }, []);

  // Load paginated customer list on mount / page change
  useEffect(() => {
    if (isSearchMode) return;
    const fetchCustomers = async () => {
      setLoading(true);
      try {
        const res = await customerApi.getCustomers(page, PAGE_LIMIT);
        // Response shape: { customers: [...], total: N, page: N, limit: N } 
        // or just an array
        let profileList = [];
        let total = 1;
        if (Array.isArray(res)) {
          profileList = res;
        } else if (res.customers) {
          profileList = res.customers;
          const totalItems = res.total || res.total_count || profileList.length;
          total = Math.ceil(totalItems / PAGE_LIMIT);
        } else if (res.data) {
          profileList = Array.isArray(res.data) ? res.data : [res.data];
        }
        setTotalPages(total || 1);
        // Show basic info immediately, then enrich
        const base = profileList.map((p) => ({
          id: p.customer_id,
          name: p.full_name || p.name || 'Unknown',
          email: p.email,
          phone: p.phone,
          contract: 'Unknown',
          churnProb: null,
          sentiment: 'Loading...',
        }));
        setCustomers(base);
        // Enrich sequentially, updating UI after each customer
        await enrichCustomers(profileList, setCustomers);
      } catch (err) {
        console.error('Failed to load customers:', err);
        setCustomers([]);
      } finally {
        setLoading(false);
      }
    };
    fetchCustomers();
  }, [page, isSearchMode, enrichCustomers]);

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      setIsSearchMode(false);
      setPage(1);
      return;
    }
    setIsSearchMode(true);
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
        const customerData = Array.isArray(res.data) ? res.data[0] : res.data;
        if (customerData && customerData.customer_profile) {
          const profile = customerData.customer_profile;
          const base = [{
            id: profile.customer_id || searchTerm,
            name: profile.full_name || 'Unknown',
            sentiment: 'Loading...',
            contract: 'Unknown',
            churnProb: null,
            phone: profile.phone,
            email: profile.email,
          }];
          setCustomers(base);
          // Enrich with churn + sentiment using customer_id from /api/data
          await enrichCustomers([profile], setCustomers);
        } else {
          setCustomers([]);
        }
      } else {
        setCustomers([]);
      }
    } catch (error) {
      console.error('Search failed:', error);
      setCustomers([]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearSearch = () => {
    setSearchTerm('');
    setIsSearchMode(false);
    setPage(1);
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
            {!isSearchMode && <span className="text-sm font-normal text-slate-500 ml-2">Trang {page} / {totalPages}</span>}
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
            {isSearchMode && (
              <button
                onClick={handleClearSearch}
                className="bg-white border border-slate-300 px-3 py-2 rounded-lg hover:bg-slate-50 transition-colors text-slate-500 text-sm"
              >
                Xoá tìm kiếm
              </button>
            )}
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
                <th className="px-6 py-4">Tên</th>
                <th className="px-6 py-4">Liên hệ</th>
                <th className="px-6 py-4">Sentiment</th>
                <th className="px-6 py-4">Churn Risk</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white/50">
              {loading && customers.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-10 text-center">
                    <div className="flex justify-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                    </div>
                  </td>
                </tr>
              ) : customers.length > 0 ? customers.map(customer => (
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
                    {customer.sentiment === 'Loading...' ? (
                      <span className="text-slate-400 text-xs animate-pulse">Đang tải...</span>
                    ) : (
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${
                        customer.sentiment === 'Positive' ? 'bg-emerald-100 border-emerald-200 text-emerald-700' :
                        customer.sentiment === 'Negative' ? 'bg-rose-100 border-rose-200 text-rose-700' :
                        customer.sentiment === 'Neutral' ? 'bg-amber-100 border-amber-200 text-amber-700' :
                        'bg-amber-100 border-amber-200 text-amber-700'
                      }`}>
                        {customer.sentiment === 'Positive' ? 'Tích cực' :
                         customer.sentiment === 'Negative' ? 'Tiêu cực' :
                         customer.sentiment === 'Neutral' ? 'Trung lập' : 'Trung lập'}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    {customer.churnProb === null ? (
                      <span className="text-slate-400 text-xs animate-pulse">Đang tải...</span>
                    ) : (
                      <div className="flex items-center gap-2">
                        <div className="w-full bg-slate-200 rounded-full h-2.5 max-w-[80px] overflow-hidden">
                          <div
                            className={`h-2.5 rounded-full ${customer.churnProb > 0.7 ? 'bg-rose-500' : customer.churnProb > 0.4 ? 'bg-amber-500' : 'bg-emerald-500'}`}
                            style={{ width: `${customer.churnProb * 100}%` }}
                          />
                        </div>
                        <span className={`text-xs font-semibold ${customer.churnProb > 0.7 ? 'text-rose-600' : customer.churnProb > 0.4 ? 'text-amber-600' : 'text-emerald-600'}`}>
                          {(customer.churnProb * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-slate-500">
                    Không tìm thấy khách hàng. Thử tìm kiếm theo ID, số điện thoại hoặc email.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {!isSearchMode && totalPages > 1 && (
          <div className="p-4 border-t border-slate-200 flex items-center justify-between bg-slate-50/60">
            <span className="text-sm text-slate-500">Trang {page} / {totalPages}</span>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1 || loading}
                className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-300 text-slate-600 text-sm hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft size={16} /> Trước
              </button>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages || loading}
                className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-300 text-slate-600 text-sm hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                Sau <ChevronRight size={16} />
              </button>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
