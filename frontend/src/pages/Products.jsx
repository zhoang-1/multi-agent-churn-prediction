import { FileSpreadsheet, Download } from 'lucide-react';

const MOCK_PRODUCTS = [
  { id: 'PRD-001', name: 'Fiber Optic 500Mbps', category: 'Internet', price: 59.99, activeSubscribers: 1245 },
  { id: 'PRD-002', name: 'Fiber Optic 1Gbps', category: 'Internet', price: 89.99, activeSubscribers: 890 },
  { id: 'PRD-003', name: 'Mobile Unlimited 5G', category: 'Mobile', price: 45.00, activeSubscribers: 3402 },
  { id: 'PRD-004', name: 'Mobile Basic 10GB', category: 'Mobile', price: 25.00, activeSubscribers: 1560 },
  { id: 'PRD-005', name: 'Premium TV Package', category: 'Television', price: 65.00, activeSubscribers: 530 },
  { id: 'PRD-006', name: 'Smart Home Security', category: 'IoT', price: 30.00, activeSubscribers: 215 },
  { id: 'PRD-007', name: 'Cloud Storage 1TB', category: 'Service', price: 9.99, activeSubscribers: 4500 },
];

export default function Products() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <FileSpreadsheet className="text-emerald-400" size={32} />
            Product Catalog
          </h1>
          <p className="text-slate-400 mt-1">Excel-like view of all offered products and services</p>
        </div>
        <button className="bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-200 px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
          <Download size={18} /> Export CSV
        </button>
      </div>

      <div className="glass rounded-xl shadow-xl overflow-hidden border border-slate-700/50">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-slate-800/80 text-slate-300 font-semibold border-b border-slate-700">
              <tr>
                <th className="px-6 py-4 border-r border-slate-700/50 w-32">Product ID</th>
                <th className="px-6 py-4 border-r border-slate-700/50">Product Name</th>
                <th className="px-6 py-4 border-r border-slate-700/50">Category</th>
                <th className="px-6 py-4 border-r border-slate-700/50 text-right">Price (USD)</th>
                <th className="px-6 py-4 text-right">Active Subscribers</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {MOCK_PRODUCTS.map((product, index) => (
                <tr 
                  key={product.id} 
                  className={`hover:bg-slate-800/40 transition-colors ${index % 2 === 0 ? 'bg-slate-900/30' : 'bg-transparent'}`}
                >
                  <td className="px-6 py-3 border-r border-slate-700/30 font-mono text-slate-400">{product.id}</td>
                  <td className="px-6 py-3 border-r border-slate-700/30 font-medium text-slate-200">{product.name}</td>
                  <td className="px-6 py-3 border-r border-slate-700/30 text-slate-300">
                    <span className="bg-slate-800 px-2 py-1 rounded text-xs border border-slate-700">{product.category}</span>
                  </td>
                  <td className="px-6 py-3 border-r border-slate-700/30 text-right text-emerald-400 font-medium">
                    ${product.price.toFixed(2)}
                  </td>
                  <td className="px-6 py-3 text-right text-slate-300">
                    {product.activeSubscribers.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
