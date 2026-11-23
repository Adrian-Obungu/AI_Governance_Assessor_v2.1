import React from 'react';

interface ErrorBoundaryProps {
    children: React.ReactNode;
}

interface ErrorBoundaryState {
    hasError: boolean;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
    state: ErrorBoundaryState = { hasError: false };

    static getDerivedStateFromError(): ErrorBoundaryState {
        return { hasError: true };
    }

    componentDidCatch(error: Error) {
        console.error('Frontend runtime error:', error);
    }

    handleReload = () => {
        window.location.reload();
    };

    render() {
        if (this.state.hasError) {
            return (
                <main className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
                    <section className="card max-w-lg w-full text-center" role="alert" aria-labelledby="runtime-error-title">
                        <p className="text-sm font-semibold uppercase tracking-wide text-primary-600">Application error</p>
                        <h1 id="runtime-error-title" className="mt-2 text-2xl font-bold text-gray-900">The assessment interface could not load</h1>
                        <p className="mt-3 text-gray-600">
                            Refresh the page to retry. If the problem continues after a Docker rebuild, clear this site&apos;s cached data and service worker, then try again.
                        </p>
                        <button type="button" onClick={this.handleReload} className="btn-primary mt-6">
                            Refresh application
                        </button>
                    </section>
                </main>
            );
        }

        return this.props.children;
    }
}
