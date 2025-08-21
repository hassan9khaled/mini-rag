import toast from 'react-hot-toast';

export const showProjectToast = (msg: string, type: 'success' | 'error' = 'success') => {
  if (type === 'success') toast.success(msg);
  else toast.error(msg);
};