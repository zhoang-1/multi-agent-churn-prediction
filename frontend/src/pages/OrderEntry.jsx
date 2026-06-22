import { useState } from 'react';
import { ShoppingCart, Plus, Trash2, Save } from 'lucide-react';

const MOCK_PRODUCTS = [
  { id: 'PRD-001', name: 'Fiber Optic 500Mbps', price: 59.99 },
  { id: 'PRD-002', name: 'Fiber Optic 1Gbps', price: 89.99 },
  { id: 'PRD-003', name: 'Mobile Unlimited 5G', price: 45.00 },
  { id: 'PRD-004', name: 'Mobile Basic 10GB', price: 25.00 },
  { id: 'PRD-005', name: 'Premium TV Package', price: 65.00 },
];

export default function OrderEntry() {
  const [orderForm, setOrderForm] = useState({
    orderId: '',
    customerId: '',
    date: new Date().toISOString().split('T')[0],
  });

  const [cart, setCart] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(MOCK_PRODUCTS[0].id);
  const [quantity, setQuantity] = useState(1);

  const addToCart = () => {
    const product = MOCK_PRODUCTS.find(p => p.id === selectedProduct);
    if (product) {
      setCart([...cart, { ...product, quantity: parseInt(quantity) }]);
      setQuantity(1);
    }
  };

  const removeFromCart = (index) => {
    setCart(cart.filter((_, i) => i !== index));
  };

  const handleOrderSubmit = (e) => {
    e.preventDefault();
    if (cart.length === 0) {
      alert("Please add at least one product to the order.");
      return;
    }
    alert(`Order ${orderForm.orderId} submitted for Customer ${orderForm.customerId} with ${cart.length} items!`);
    setOrderForm({ ...orderForm, orderId: '', customerId: '' });
    setCart([]);
  };

  const totalAmount = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <ShoppingCart className="text-indigo-400" size={32} />
          Order Entry
        </h1>
        <p className="text-slate-400">Create new orders for customers</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Order Details Form */}
        <div className="glass p-6 rounded-2xl shadow-lg border border-slate-700/50 col-span-1">
          <h2 className="text-xl font-semibold mb-6">Order Information</h2>
          <form className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Order ID</label>
              <input 
                type="text" 
                placeholder="e.g. ORD-9001"
                value={orderForm.orderId}
                onChange={e => setOrderForm({...orderForm, orderId: e.target.value})}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:ring-2 focus:ring-indigo-500 outline-none" required 
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Customer ID</label>
              <input 
                type="text" 
                placeholder="e.g. CUS-1001"
                value={orderForm.customerId}
                onChange={e => setOrderForm({...orderForm, customerId: e.target.value})}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:ring-2 focus:ring-indigo-500 outline-none" required 
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Date</label>
              <input 
                type="date" 
                value={orderForm.date}
                onChange={e => setOrderForm({...orderForm, date: e.target.value})}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:ring-2 focus:ring-indigo-500 outline-none" required 
              />
            </div>
          </form>
        </div>

        {/* Product Selection & Cart */}
        <div className="glass p-6 rounded-2xl shadow-lg border border-slate-700/50 col-span-1 lg:col-span-2 flex flex-col">
          <h2 className="text-xl font-semibold mb-6">Add Products</h2>
          
          <div className="flex gap-4 mb-6">
            <div className="flex-1">
              <select 
                value={selectedProduct}
                onChange={e => setSelectedProduct(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:ring-2 focus:ring-indigo-500 outline-none appearance-none"
              >
                {MOCK_PRODUCTS.map(p => (
                  <option key={p.id} value={p.id}>{p.name} - ${p.price}</option>
                ))}
              </select>
            </div>
            <div className="w-24">
              <input 
                type="number" min="1"
                value={quantity}
                onChange={e => setQuantity(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:ring-2 focus:ring-indigo-500 outline-none text-center"
              />
            </div>
            <button 
              type="button"
              onClick={addToCart}
              className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
            >
              <Plus size={18} /> Add
            </button>
          </div>

          <div className="flex-1 bg-slate-900/50 rounded-lg border border-slate-700/50 p-4 overflow-y-auto min-h-[200px]">
            {cart.length === 0 ? (
              <div className="h-full flex items-center justify-center text-slate-500 italic">
                Cart is empty. Add products above.
              </div>
            ) : (
              <table className="w-full text-left text-sm">
                <thead className="text-slate-400 border-b border-slate-700">
                  <tr>
                    <th className="pb-2 font-medium">Product</th>
                    <th className="pb-2 font-medium text-right">Qty</th>
                    <th className="pb-2 font-medium text-right">Unit Price</th>
                    <th className="pb-2 font-medium text-right">Total</th>
                    <th className="pb-2"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {cart.map((item, index) => (
                    <tr key={index} className="hover:bg-slate-800/30">
                      <td className="py-3 text-slate-200">{item.name}</td>
                      <td className="py-3 text-right">{item.quantity}</td>
                      <td className="py-3 text-right">${item.price.toFixed(2)}</td>
                      <td className="py-3 text-right text-emerald-400 font-medium">${(item.price * item.quantity).toFixed(2)}</td>
                      <td className="py-3 text-right">
                        <button onClick={() => removeFromCart(index)} className="text-rose-400 hover:text-rose-300 p-1">
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div className="mt-6 flex items-center justify-between border-t border-slate-700/50 pt-4">
            <div>
              <p className="text-slate-400 text-sm">Total Amount</p>
              <p className="text-2xl font-bold text-emerald-400">${totalAmount.toFixed(2)}</p>
            </div>
            <button 
              onClick={handleOrderSubmit}
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-2.5 px-6 rounded-lg flex items-center gap-2 transition-colors shadow-lg shadow-emerald-500/20"
            >
              <Save size={20} /> Submit Order
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
