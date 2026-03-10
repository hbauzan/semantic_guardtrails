import React from 'react';
import ArithmeticHUD from './components/ArithmeticHUD';

const App: React.FC = () => {
  return (
    <div style={{ width: '100vw', height: '100vh', background: '#050505', overflow: 'hidden' }}>
      <ArithmeticHUD />
    </div>
  );
};

export default App;
