import { AuthenticationEvent } from './authentication-event';
import SessionExpiredEventPayload from './definitions/session-expired-event-payload';

export interface AuthenticationEventMap {
  [AuthenticationEvent.SESSION_EXPIRED]: SessionExpiredEventPayload;
}
