import { useState } from 'react';
import { UserPlus, ReceiptText, Save } from 'lucide-react';

export default function DataEntry() {
  const [customerForm, setCustomerForm] = useState({
    customerId: '',
    name: '',
    age: '',
    tenure: '',
    monthlyCharges: '',
    contractType: 'Month-to-month'
  });

  const [invoiceForm, setInvoiceForm] = useState({
    invoiceId: '',
    customerId: '',
    amount: '',
    date: ''
  });

  const handleCustomerSubmit = (e) => {
    e.preventDefault();
    alert(`Customer ${customerForm.customerId} added! (Mock)`);
    setCustomerForm({ ...customerForm, customerId: '', name: '', age: '', tenure: '', monthlyCharges: '' });
  };

  const handleInvoiceSubmit = (e) => {
    e.preventDefault();
    alert(`Invoice ${invoiceForm.invoiceId} added! (Mock)`);
    setInvoiceForm({ invoiceId: '', customerId: '', amount: '', date: '' });
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Data Entry</h1>
        <p className="text-slate-400">Manually insert records into the database</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Customer Input Form */}
        <div className="glass p-8 rounded-2xl shadow-lg border border-slate-700/50">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2 text-indigo-400">
            <UserPlus size={24} /> Add New Customer
          </h2>
          <form onSubmit={handleCustomerSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Customer ID</label>
              <input 
                type="text" 
                placeholder="e.g. CUS-1006"
                value={customerForm.customerId}
                onChange={e => setCustomerForm({...customerForm, customerId: e.target.value})}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:ring-2 focus:ring-indigo-500 outline-none" required 
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Full Name</label>
              <input 
                type="text" 
                value={customerForm.name}
                onChange={e => setCustomerForm({...customerForm, name: e.target.value})}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:ring-2 focus:ring-indigo-500 outline-none" required 
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Age</label>
                <input 
                  type="number" 
                  value={customerForm.age}
                  onChange={e => setCustomerForm({...customerForm, age: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:ring-2 focus:ring-indigo-500 outline-none" required 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Tenure (mos)</label>
                <input 
                  type="number" 
                  value={customerForm.tenure}
                  onChange={e => setCustomerForm({...customerForm, tenure: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:ring-2 focus:ring-indigo-500 outline-none" required 
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Monthly $</label>
                <input 
                  type="number" step="0.01"
                  value={customerForm.monthlyCharges}
                  onChange={e => setCustomerForm({...customerForm, monthlyCharges: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:ring-2 focus:ring-indigo-500 outline-none" required 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Contract</label>
                <select 
                  value={customerForm.contractType}
                  onChange={e => setCustomerForm({...customerForm, contractType: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:ring-2 focus:ring-indigo-500 outline-none"
                >
                  <option>Month-to-month</option>
                  <option>One year</option>
                  <option>Two year</option>
                </select>
              </div>
            </div>
            <button type="submit" className="w-full mt-4 bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2.5 rounded-lg flex items-center justify-center gap-2 transition-colors">
              <Save size={18} /> Save Customer
            </button>
          </form>
        </div>

        {/* Invoice Input Form */}
        <div className="glass p-8 rounded-2xl shadow-lg border border-slate-700/50">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2 text-cyan-400">
            <ReceiptText size={24} /> Log Transaction/Invoice
          </h2>
          <form onSubmit={handleInvoiceSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Invoice ID</label>
              <input 
                type="text" 
                placeholder="e.g. INV-2001"
                value={invoiceForm.invoiceId}
                onChange={e => setInvoiceForm({...invoiceForm, invoiceId: e.target.value})}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:ring-2 focus:ring-cyan-500 outline-none" required 
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Customer ID</label>
              <input 
                type="text" 
                placeholder="e.g. CUS-1001"
                value={invoiceForm.customerId}
                onChange={e => setInvoiceForm({...invoiceForm, customerId: e.target.value})}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:ring-2 focus:ring-cyan-500 outline-none" required 
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Amount ($)</label>
                <input 
                  type="number" step="0.01"
                  value={invoiceForm.amount}
                  onChange={e => setInvoiceForm({...invoiceForm, amount: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:ring-2 focus:ring-cyan-500 outline-none" required 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Date</label>
                <input 
                  type="date" 
                  value={invoiceForm.date}
                  onChange={e => setInvoiceForm({...invoiceForm, date: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:ring-2 focus:ring-cyan-500 outline-none" required 
                />
              </div>
            </div>
            <div className="pt-2">
              <p className="text-xs text-slate-500 mb-4">* Ensure Customer ID exists before logging a transaction.</p>
              <button type="submit" className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-medium py-2.5 rounded-lg flex items-center justify-center gap-2 transition-colors">
                <Save size={18} /> Log Transaction
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
