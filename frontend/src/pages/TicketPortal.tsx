import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Wrench, CheckCircle2, AlertCircle } from 'lucide-react';
import { submitTicket } from '../api';
import { useMutation } from '@tanstack/react-query';

const ISSUE_TYPES = ["Flat Tire", "Broken Chain", "Brakes Loose", "Gears Skipping", "Saddle Stolen", "Other"];

export default function TicketPortal() {
  const [bikeId, setBikeId] = useState('');
  const [issueType, setIssueType] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    // Check URL for pre-filled bike ID (QR code flow)
    const params = new URLSearchParams(window.location.search);
    if (params.get('bike_id')) {
      setBikeId(params.get('bike_id')!);
    }
  }, []);

  const mutation = useMutation({
    mutationFn: submitTicket,
    onSuccess: () => {
      setStatus('success');
      setTimeout(() => {
        setStatus('idle');
        setBikeId('');
        setIssueType('');
        setDescription('');
      }, 3000);
    },
    onError: (error: any) => {
      setStatus('error');
      setErrorMsg(error.message);
      setTimeout(() => setStatus('idle'), 4000);
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!bikeId || !issueType) return;
    mutation.mutate({ bike_id: parseInt(bikeId), issue_type: issueType, description });
  };

  return (
    <div className="max-w-xl mx-auto px-6 py-20">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-3xl p-8 sm:p-12 relative overflow-hidden"
      >
        <div className="absolute top-0 right-0 -mr-16 -mt-16 text-slate-100 opacity-50 z-0 pointer-events-none">
          <Wrench size={200} />
        </div>

        <div className="relative z-10">
          <h1 className="text-4xl font-extrabold tracking-tight mb-2">Report an Issue</h1>
          <p className="text-slate-500 mb-8">Scan a QR code or manually enter the bike details below.</p>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-semibold mb-2">Bike ID</label>
              <input 
                type="number" 
                value={bikeId}
                onChange={e => setBikeId(e.target.value)}
                required
                className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-4 py-4 focus:ring-2 focus:ring-accent focus:border-accent transition-all text-lg font-medium outline-none"
                placeholder="e.g. 1"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">What's wrong?</label>
              <div className="grid grid-cols-2 gap-3">
                {ISSUE_TYPES.map(type => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => setIssueType(type)}
                    className={`px-4 py-3 rounded-xl border text-sm font-medium transition-all ${
                      issueType === type 
                      ? 'bg-accent border-accent text-white shadow-lg shadow-accent/30' 
                      : 'bg-white border-slate-200 hover:border-slate-300 text-slate-700'
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Additional Details</label>
              <textarea 
                value={description}
                onChange={e => setDescription(e.target.value)}
                className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-4 py-4 focus:ring-2 focus:ring-accent focus:border-accent transition-all resize-none outline-none"
                rows={3}
                placeholder="Tell us exactly what happened..."
              />
            </div>

            <button 
              type="submit" 
              disabled={mutation.isPending || !bikeId || !issueType}
              className="w-full bg-slate-900 text-white rounded-xl py-4 font-bold text-lg hover:bg-slate-800 transition-colors disabled:opacity-50 flex justify-center items-center h-14"
            >
              {mutation.isPending ? 'Submitting...' : 'Submit Ticket'}
            </button>
          </form>
        </div>
      </motion.div>

      {/* Toasts */}
      <motion.div 
        initial={{ opacity: 0, y: 50, scale: 0.9 }}
        animate={{ opacity: status !== 'idle' ? 1 : 0, y: status !== 'idle' ? 0 : 50, scale: status !== 'idle' ? 1 : 0.9 }}
        className="fixed bottom-8 left-0 right-0 flex justify-center pointer-events-none z-50 px-4"
      >
        {status === 'success' && (
          <div className="bg-emerald-500 text-white px-6 py-4 rounded-2xl shadow-2xl flex items-center space-x-3 font-semibold">
            <CheckCircle2 />
            <span>Ticket submitted successfully!</span>
          </div>
        )}
        {status === 'error' && (
          <div className="bg-rose-500 text-white px-6 py-4 rounded-2xl shadow-2xl flex items-center space-x-3 font-semibold">
            <AlertCircle />
            <span>{errorMsg}</span>
          </div>
        )}
      </motion.div>
    </div>
  );
}
