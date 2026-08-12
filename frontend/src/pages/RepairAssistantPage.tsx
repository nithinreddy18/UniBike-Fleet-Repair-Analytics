
import { ChatAssistant } from './AdminDashboard';

export default function RepairAssistantPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-10 h-[calc(100vh-80px)]">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-extrabold tracking-tight mb-2">DIY Repair Assistant</h1>
        <p className="text-slate-500">Search the UniBike maintenance manuals to fix minor issues yourself!</p>
      </div>
      <div className="h-full glass rounded-3xl p-2 sm:p-6 shadow-2xl">
        <ChatAssistant />
      </div>
    </div>
  );
}
