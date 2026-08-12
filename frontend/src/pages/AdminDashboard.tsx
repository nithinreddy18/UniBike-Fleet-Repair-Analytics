import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { fetchKpi, chatAssistant } from '../api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { LayoutDashboard, MessageSquare, AlertTriangle, CheckCircle, Package, Send, Loader2, Ticket } from 'lucide-react';
import { fetchTickets, updateTicketStatus } from '../api';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState<'kpi' | 'chat' | 'tickets'>('kpi');

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex flex-col md:flex-row gap-8 h-[calc(100vh-80px)]">
      {/* Sidebar */}
      <div className="w-full md:w-64 flex flex-col space-y-2">
        <button 
          onClick={() => setActiveTab('kpi')}
          className={`flex items-center space-x-3 px-4 py-3 rounded-xl font-semibold transition-all ${
            activeTab === 'kpi' ? 'bg-slate-900 text-white shadow-lg' : 'hover:bg-slate-100 text-slate-600'
          }`}
        >
          <LayoutDashboard size={20} />
          <span>KPI Dashboard</span>
        </button>
        <button 
          onClick={() => setActiveTab('tickets')}
          className={`flex items-center space-x-3 px-4 py-3 rounded-xl font-semibold transition-all ${
            activeTab === 'tickets' ? 'bg-slate-900 text-white shadow-lg' : 'hover:bg-slate-100 text-slate-600'
          }`}
        >
          <Ticket size={20} />
          <span>Manage Tickets</span>
        </button>
        <button 
          onClick={() => setActiveTab('chat')}
          className={`flex items-center space-x-3 px-4 py-3 rounded-xl font-semibold transition-all ${
            activeTab === 'chat' ? 'bg-slate-900 text-white shadow-lg' : 'hover:bg-slate-100 text-slate-600'
          }`}
        >
          <MessageSquare size={20} />
          <span>Repair Assistant</span>
        </button>
      </div>

      {/* Main Content Area */}
      <div className="flex-grow glass rounded-3xl p-8 overflow-y-auto">
        <AnimatePresence mode="wait">
          {activeTab === 'kpi' ? (
            <motion.div
              key="kpi"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="h-full"
            >
              <KpiDashboard onNavigateToTickets={() => setActiveTab('tickets')} />
            </motion.div>
          ) : activeTab === 'chat' ? (
            <motion.div
              key="chat"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="h-full flex flex-col"
            >
              <ChatAssistant />
            </motion.div>
          ) : (
            <motion.div
              key="tickets"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="h-full"
            >
              <ManageTickets />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

function KpiDashboard({ onNavigateToTickets }: { onNavigateToTickets: () => void }) {
  const { data, isLoading, error } = useQuery({ queryKey: ['kpi'], queryFn: fetchKpi, refetchInterval: 5000 });

  if (isLoading) return <div className="flex justify-center items-center h-full"><Loader2 className="animate-spin text-accent" size={48} /></div>;
  if (error) return <div className="text-rose-500">Error loading KPIs</div>;

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-extrabold tracking-tight mb-6">Fleet Status Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100 flex items-center space-x-4">
            <div className="p-4 bg-emerald-100 text-emerald-600 rounded-xl"><CheckCircle size={28} /></div>
            <div>
              <p className="text-slate-500 font-semibold text-sm">MTTR (Days)</p>
              <p className="text-3xl font-black">{data.metrics.mttr}</p>
            </div>
          </div>
          <div 
            onClick={onNavigateToTickets}
            className="bg-slate-50 p-6 rounded-2xl border border-slate-100 flex items-center space-x-4 cursor-pointer hover:bg-slate-100 transition-colors shadow-sm hover:shadow-md"
          >
            <div className="p-4 bg-amber-100 text-amber-600 rounded-xl"><AlertTriangle size={28} /></div>
            <div>
              <p className="text-slate-500 font-semibold text-sm">Open Tickets</p>
              <p className="text-3xl font-black">{data.metrics.open_tickets}</p>
            </div>
          </div>
          <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100 flex items-center space-x-4">
            <div className="p-4 bg-rose-100 text-rose-600 rounded-xl"><Package size={28} /></div>
            <div>
              <p className="text-slate-500 font-semibold text-sm">Missed SLAs</p>
              <p className="text-3xl font-black">{data.metrics.missed_slas}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h3 className="text-xl font-bold mb-4 text-slate-700">Work Order Distribution</h3>
          <div className="h-64 bg-slate-50 p-4 rounded-2xl border border-slate-100">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.status_distribution}>
                <XAxis dataKey="status" tick={{ fill: '#64748b' }} axisLine={false} tickLine={false} />
                <Tooltip cursor={{fill: 'transparent'}} contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }} />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {data.status_distribution.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.status === 'Open' ? '#ef4444' : entry.status === 'Resolved' ? '#10b981' : '#f59e0b'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div>
          <h3 className="text-xl font-bold mb-4 text-slate-700">Critical Inventory Levels</h3>
          <div className="h-64 bg-slate-50 p-4 rounded-2xl border border-slate-100 overflow-y-auto">
             <div className="space-y-3">
              {data.inventory.map((item: any) => {
                const isLow = item.quantity <= item.reorder_level;
                return (
                  <div key={item.part_name} className="flex justify-between items-center p-3 bg-white rounded-xl shadow-sm border border-slate-50">
                    <span className="font-semibold">{item.part_name}</span>
                    <div className="flex items-center space-x-3">
                      <span className={`text-sm font-bold px-2 py-1 rounded-md ${isLow ? 'bg-rose-100 text-rose-700' : 'bg-slate-100 text-slate-600'}`}>
                        {item.quantity} / {item.reorder_level}
                      </span>
                      {isLow && <span className="flex h-2 w-2 rounded-full bg-rose-500 animate-pulse"></span>}
                    </div>
                  </div>
                )
              })}
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ManageTickets() {
  const { data: tickets, isLoading, refetch } = useQuery({ queryKey: ['tickets'], queryFn: fetchTickets, refetchInterval: 5000 });
  
  const handleStatusChange = async (ticketId: number, newStatus: string) => {
    try {
      await updateTicketStatus(ticketId, newStatus);
      refetch();
    } catch (e) {
      console.error(e);
      alert("Failed to update status");
    }
  };

  if (isLoading) return <div className="flex justify-center items-center h-full"><Loader2 className="animate-spin text-accent" size={48} /></div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-extrabold tracking-tight">Manage Tickets</h2>
        <span className="bg-slate-900 text-white px-3 py-1 rounded-full text-sm font-bold">{tickets?.length || 0} Total</span>
      </div>

      <div className="bg-white border border-slate-100 shadow-sm rounded-2xl overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-slate-50 border-b border-slate-100 text-slate-500 font-semibold text-sm uppercase">
            <tr>
              <th className="p-4">Ticket ID</th>
              <th className="p-4">Bike ID</th>
              <th className="p-4">Issue</th>
              <th className="p-4">Description</th>
              <th className="p-4">Date</th>
              <th className="p-4">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {tickets?.map((t: any) => (
              <tr key={t.id} className="hover:bg-slate-50 transition-colors">
                <td className="p-4 font-bold text-slate-700">#{t.id}</td>
                <td className="p-4 font-semibold text-accent">Bike {t.bike_id}</td>
                <td className="p-4 font-medium">{t.issue_type}</td>
                <td className="p-4 text-slate-500 text-sm max-w-xs truncate" title={t.description}>{t.description || '-'}</td>
                <td className="p-4 text-slate-500 text-sm">{new Date(t.created_at).toLocaleDateString()}</td>
                <td className="p-4">
                  <select 
                    value={t.status} 
                    onChange={(e) => handleStatusChange(t.id, e.target.value)}
                    className={`text-sm font-bold px-3 py-1.5 rounded-lg border outline-none cursor-pointer transition-colors ${
                      t.status === 'Open' ? 'bg-rose-50 text-rose-700 border-rose-200' :
                      t.status === 'In Progress' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                      'bg-emerald-50 text-emerald-700 border-emerald-200'
                    }`}
                  >
                    <option value="Open">Open</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Resolved">Resolved</option>
                  </select>
                </td>
              </tr>
            ))}
            {tickets?.length === 0 && (
              <tr>
                <td colSpan={6} className="p-8 text-center text-slate-500">No tickets found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function ChatAssistant() {
  const [messages, setMessages] = useState<Array<{role: 'user' | 'assistant', content: string, sources?: string[]}>>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsLoading(true);

    try {
      const res = await chatAssistant(userMsg);
      setMessages(prev => [...prev, { role: 'assistant', content: res.answer, sources: res.sources }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I encountered an error. Please try again." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-50 rounded-2xl border border-slate-100 overflow-hidden">
      <div className="bg-slate-900 text-white px-6 py-4">
        <h3 className="font-bold text-lg flex items-center space-x-2"><MessageSquare size={18}/> <span>AI Repair Assistant</span></h3>
        <p className="text-slate-400 text-sm">Ask me how to fix specific UniBike issues.</p>
      </div>
      
      <div className="flex-grow p-6 overflow-y-auto space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex items-center justify-center text-slate-400">
            <p>Start typing to search repair manuals...</p>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-4 rounded-2xl ${m.role === 'user' ? 'bg-accent text-white rounded-br-sm' : 'bg-white shadow-sm border border-slate-100 rounded-bl-sm'}`}>
              <p>{m.content}</p>
              {m.sources && m.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-100 text-sm">
                  <p className="text-slate-500 font-semibold mb-1">Sources:</p>
                  <ul className="list-disc pl-4 space-y-1 text-slate-600 text-xs">
                    {m.sources.map((s, idx) => <li key={idx} className="truncate" title={s}>{s}</li>)}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white shadow-sm border border-slate-100 p-4 rounded-2xl rounded-bl-sm flex space-x-2">
               <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
               <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
               <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 bg-white border-t border-slate-100">
        <form onSubmit={handleSend} className="relative">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="e.g., How do I tighten the Shimano Nexus brakes?"
            className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-4 pr-12 py-4 focus:ring-2 focus:ring-accent focus:border-accent transition-all outline-none"
          />
          <button 
            type="submit"
            disabled={isLoading || !input.trim()}
            className="absolute right-2 top-2 bottom-2 bg-accent text-white p-2 rounded-lg hover:bg-accent-hover transition-colors disabled:opacity-50"
          >
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
}
