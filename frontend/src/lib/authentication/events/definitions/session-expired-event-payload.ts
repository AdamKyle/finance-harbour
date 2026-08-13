export enum SessionExpiredReason {
  REFRESH_FAILED = 'REFRESH_FAILED',
  REPEATED_UNAUTHORIZED = 'REPEATED_UNAUTHORIZED',
}

export default interface SessionExpiredEventPayload {
  reason: SessionExpiredReason;
}
