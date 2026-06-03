interface Props {
  message: string;
  onRetry?: () => void;
}

export function ErrorPanel({ message, onRetry }: Props) {
  return (
    <div className="panel error-panel" role="alert">
      <p>{message}</p>
      {onRetry && (
        <button type="button" className="btn" onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  );
}
