export const parseLocalIsoDate = (isoDate: string): Date => {
  return new Date(`${isoDate}T12:00:00`);
};

export const formatLocalIsoDate = (date: Date): string => {
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, '0');
  const day = `${date.getDate()}`.padStart(2, '0');

  return `${year}-${month}-${day}`;
};

export const getDayAfterLocalIsoDate = (isoDate: string): Date => {
  const date = parseLocalIsoDate(isoDate);
  date.setDate(date.getDate() + 1);

  return date;
};
