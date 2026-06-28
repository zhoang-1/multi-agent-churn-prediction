import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, AlertTriangle, CheckCircle, 
  TrendingDown, TrendingUp, Activity,
  MessageSquare, FileText, ShoppingBag, ShieldAlert,
  Zap
} from 'lucide-react';
import { customerApi } from '../services/api';

export default function CustomerDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  

  const [customerInfo, setCustomerInfo] = useState(null);
  const [orders, setOrders] = useState([]);
  const [churnProb, setChurnProb] = useState(0.15); 
  const [sentiment, setSentiment] = useState('Neutral');
  const [report, setReport] = useState('Đang tải báo cáo...');
  const [actionPlan, setActionPlan] = useState('');

  useEffect(() => {
    const fetchCustomerData = async () => {
      setLoading(true);
      const query = { customer_id: id };

      // Run /data and /report in parallel
      const [dataRes, reportRes] = await Promise.allSettled([
        customerApi.getData(query),
        customerApi.getReport(query),
      ]);

      // --- /data: thông tin khách hàng + đơn hàng ---
      try {
        const d = dataRes.status === 'fulfilled' ? dataRes.value : null;
        if (d?.data) {
          const customerData = Array.isArray(d.data) ? d.data[0] : d.data;
          if (customerData?.customer_profile) {
            const profile = customerData.customer_profile;
            setCustomerInfo({
              name: profile.full_name || 'Unknown',
              email: profile.email || '',
              phone: profile.phone || '',
              address: profile.address || null,
            });
            setOrders(profile.orders || []);
          }
        }
      } catch (e) { console.warn('/data parse error', e); }

      // --- /report: bao gồm sentiment + churn + báo cáo + hành động ---
      try {
        const r = reportRes.status === 'fulfilled' ? reportRes.value : null;
        if (r?.report) {
          const reportData = r.report;

          // Lấy sentiment từ report
          if (reportData.sentiment_result?.label) {
            const label = reportData.sentiment_result.label;
            setSentiment(label.charAt(0).toUpperCase() + label.slice(1));
          }

          // Lấy churn từ report
          if (reportData.churn_result?.churn_probability !== undefined) {
            setChurnProb(reportData.churn_result.churn_probability);
          }

          // Lấy nội dung báo cáo
          if (reportData.report) {
            setReport(reportData.report);
          }

          // Lấy hành động khuyến nghị
          if (reportData.action_plan?.detail) {
            setActionPlan(reportData.action_plan.detail);
          }
        } else {
          setReport('Không thể tải báo cáo từ API.');
          setActionPlan('Không có hành động khuyến nghị nào.');
        }
      } catch (e) {
        console.warn('/report parse error', e);
        setReport('Lỗi khi tải báo cáo.');
      }

      setLoading(false);
    };

    if (id) {
      fetchCustomerData();
    }
  }, [id]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 text-red-600 p-6 rounded-lg text-center">
        <AlertTriangle className="mx-auto mb-2" size={32} />
        <p className="font-medium">{error}</p>
        <button onClick={() => navigate(-1)} className="mt-4 text-indigo-600 hover:underline">Quay lại</button>
      </div>
    );
  }

  return (
    <div className="space-y-6 text-slate-800 pb-12">
      <div className="flex items-center gap-4">
        <button 
          onClick={() => navigate(-1)}
          className="p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-600"
        >
          <ArrowLeft size={24} />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Chi Tiết Khách Hàng</h1>
          <p className="text-slate-500 font-mono mt-1">ID: {id}</p>
        </div>
      </div>

      {/* Thông tin cơ bản */}
      {customerInfo && (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col md:flex-row gap-8 justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-slate-800 mb-2">{customerInfo.name}</h2>
            <div className="space-y-1 text-slate-600 text-sm">
              <p>Email: {customerInfo.email}</p>
              <p>Phone: {customerInfo.phone}</p>
              {customerInfo.address && (
                <p>Địa chỉ: {customerInfo.address.street}, {customerInfo.address.ward}, {customerInfo.address.district}, {customerInfo.address.city}</p>
              )}
            </div>
          </div>
          
          <div className="flex gap-4">
             {/* Tỷ lệ rời bỏ (Churn Rate) */}
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 min-w-[160px] flex flex-col justify-center items-center">
              <p className="text-slate-500 text-xs font-semibold uppercase mb-2 text-center w-full">Tỷ lệ rời bỏ</p>
              <div className="flex items-center justify-center gap-2">
                {churnProb > 0.7 ? <TrendingDown size={24} className="text-rose-500" /> : <TrendingUp size={24} className="text-emerald-500" />}
                <span className={`text-3xl font-bold ${churnProb > 0.7 ? 'text-rose-600' : churnProb > 0.4 ? 'text-amber-500' : 'text-emerald-600'}`}>
                  {(churnProb * 100).toFixed(0)}%
                </span>
              </div>
              <p className={`text-xs mt-2 font-medium ${churnProb > 0.7 ? 'text-rose-600' : churnProb > 0.4 ? 'text-amber-600' : 'text-emerald-600'}`}>
                {churnProb > 0.7 ? 'Nguy cơ cao' : churnProb > 0.4 ? 'Nguy cơ trung bình' : 'An toàn'}
              </p>
            </div>
            
            {/* Phân tích trải nghiệm (Experience Analysis) */}
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 min-w-[160px] flex flex-col justify-center items-center">
               <p className="text-slate-500 text-xs font-semibold uppercase mb-2 text-center w-full">Trải nghiệm</p>
               <div className="flex items-center justify-center gap-2">
                 {sentiment === 'Negative' ? <AlertTriangle size={24} className="text-rose-500" /> : <CheckCircle size={24} className="text-emerald-500" />}
                 <span className={`text-xl font-bold ${
                    sentiment === 'Positive' ? 'text-emerald-600' :
                    sentiment === 'Negative' ? 'text-rose-600' : 'text-amber-500'
                  }`}>
                    {sentiment === 'Positive' ? 'Tích cực' : sentiment === 'Negative' ? 'Tiêu cực' : 'Trung lập'}
                 </span>
               </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Báo cáo tổng hợp */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col">
           <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-indigo-700">
              <FileText size={20} /> Báo cáo tổng hợp
           </h3>
           <div className="bg-indigo-50/50 p-4 rounded-xl border border-indigo-100 text-slate-700 text-sm leading-relaxed whitespace-pre-wrap flex-1 overflow-y-auto max-h-80">
              {report}
           </div>
        </div>

        {/* Hành động với khách hàng (Action with customer) */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col">
           <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-emerald-600">
              <Zap size={20} /> Hành động khuyến nghị
           </h3>
           
           <div className="bg-emerald-50 p-4 rounded-xl border border-emerald-100 mb-4 flex-1 overflow-y-auto max-h-64">
             <p className="text-emerald-800 text-sm font-medium whitespace-pre-wrap">
               {actionPlan || (churnProb > 0.7 
                 ? "Khách hàng có nguy cơ rời bỏ cao. Cần liên hệ ngay lập tức để tìm hiểu nguyên nhân và đưa ra voucher giảm giá 30% cho đơn hàng tiếp theo."
                 : "Khách hàng đang có trải nghiệm tốt. Đề xuất gửi email cảm ơn và giới thiệu chương trình khách hàng thân thiết.")}
             </p>
           </div>
           
           <div className="flex gap-3 mt-auto pt-2">
             <button className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-2.5 rounded-lg transition-colors font-medium text-sm flex justify-center items-center gap-2">
                <MessageSquare size={16} /> Gửi Email Hỗ Trợ
             </button>
             <button className="flex-1 bg-white border border-indigo-200 text-indigo-600 hover:bg-indigo-50 py-2.5 rounded-lg transition-colors font-medium text-sm">
                Áp Dụng Khuyến Mãi
             </button>
           </div>
        </div>
      </div>

      {/* Danh sách đơn hàng (Order List) */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
         <div className="p-5 border-b border-slate-200 flex items-center bg-slate-50/80">
            <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
              <ShoppingBag className="text-indigo-600" size={20} /> Danh Sách Đơn Hàng
            </h3>
         </div>
         <div className="overflow-x-auto">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="bg-slate-50 text-slate-500 uppercase text-xs font-semibold">
                <tr>
                  <th className="px-6 py-4">Mã ĐH</th>
                  <th className="px-6 py-4">Ngày Mua</th>
                  <th className="px-6 py-4">Sản Phẩm</th>
                  <th className="px-6 py-4">Tổng Tiền</th>
                  <th className="px-6 py-4">Trạng Thái</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {orders.map((order, idx) => (
                  <tr key={order.order_id || idx} className="hover:bg-slate-50/50">
                    <td className="px-6 py-4 font-mono text-indigo-600">{order.order_id}</td>
                    <td className="px-6 py-4 text-slate-600">
                       {order.order_date ? new Date(order.order_date).toLocaleDateString('vi-VN') : 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-slate-700">
                      {order.items && order.items.length > 0 ? (
                        <span>
                          {order.items[0].product_name} 
                          {order.items.length > 1 && <span className="text-slate-400 text-xs ml-1">(+{order.items.length - 1} nữa)</span>}
                        </span>
                      ) : 'Không có thông tin'}
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-800">
                       {order.payment?.total_amount ? order.payment.total_amount.toLocaleString('vi-VN') + ' đ' : 'N/A'}
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 rounded-full text-xs font-medium border bg-blue-50 text-blue-700 border-blue-200">
                        {order.status || 'Hoàn tất'}
                      </span>
                    </td>
                  </tr>
                ))}
                {orders.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-6 py-8 text-center text-slate-500">
                      Không có đơn hàng nào được tìm thấy.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
         </div>
      </div>
    </div>
  );
}
