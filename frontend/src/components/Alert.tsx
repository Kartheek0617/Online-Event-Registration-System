import React from 'react';

interface AlertProps {
  type: 'danger' | 'success' | 'warning' | 'info';
  message: string;
  onClose?: () => void;
}

export const Alert: React.FC<AlertProps> = ({ type, message, onClose }) => {
  if (!message) return null;

  return (
    <div className={`alert alert-${type}`} role="alert">
      <span style={{ flex: 1 }}>{message}</span>
      {onClose && (
        <button
          onClick={onClose}
          style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', fontWeight: 'bold' }}
          aria-label="Dismiss alert"
        >
          &times;
        </button>
      )}
    </div>
  );
};
