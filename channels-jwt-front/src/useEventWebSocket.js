import { useCallback, useEffect, useRef } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";

export default function useEventWebSocket(url, options, connect) {
  const { lastJsonMessage, sendJsonMessage, readyState } = useWebSocket(
    url,
    options,
    connect
  );
  const listenersRef = useRef({});

  const onEvent = useCallback((event, listener) => {
    listenersRef.current = {
      ...listenersRef.current,
      [event]: [...(listenersRef.current[event] || []), listener],
    };
  }, []);

  const removeEvent = useCallback((event, listener) => {
    // TODO: implement
    // listenersRef.current = {
    //   ...listenersRef.current,
    //   [event]: [...(listenersRef.current[event] || []), listener],
    // };
  }, []);

  useEffect(() => {
    if (lastJsonMessage !== null) {
      listenersRef.current[lastJsonMessage.event].forEach((listener) =>
        listener(lastJsonMessage.payload)
      );
    }
  }, [lastJsonMessage]);

  const sendEvent = useCallback(
    (event, payload) => {
      sendJsonMessage({
        event,
        payload,
      });
    },
    [sendJsonMessage]
  );

  return { lastJsonMessage, readyState, sendEvent, onEvent, removeEvent };
}

export const connectionStatus = {
  [ReadyState.CONNECTING]: "Connecting",
  [ReadyState.OPEN]: "Open",
  [ReadyState.CLOSING]: "Closing",
  [ReadyState.CLOSED]: "Closed",
  [ReadyState.UNINSTANTIATED]: "Uninstantiated",
};

export function getConnectionStatus(readyState) {
  return connectionStatus[readyState] || "Unknown";
}
