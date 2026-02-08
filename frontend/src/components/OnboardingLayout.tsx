import { Outlet } from 'react-router';

export function OnboardingLayout() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <header className="bg-[#4A3B7A] text-white px-6 py-4 shadow-md">
        <div className="max-w-7xl mx-auto flex items-center gap-3">
          <div className="w-8 h-8 bg-[#7C6BAD] rounded flex items-center justify-center font-bold">
            W
          </div>
          <span className="text-xl">Chesster</span>
        </div>
      </header>
      <main className="max-w-4xl mx-auto px-6 py-12">
        <Outlet />
      </main>
    </div>
  );
}
