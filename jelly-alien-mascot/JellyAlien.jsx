import React, { useEffect, useRef, useImperativeHandle, forwardRef } from 'react';
import { JellyAlienMascot } from './jelly-alien.js';

/**
 * Componente React para o Mascote Alienígena Gelatinoso ("Gloop")
 *
 * Exemplo de uso:
 *   <JellyAlien state="idle" theme="emerald" size={200} />
 */
export const JellyAlien = forwardRef(function JellyAlien(
  {
    state = 'idle',
    theme = 'emerald',
    size = 220,
    squishFactor = 1.0,
    followCursor = true,
    className = '',
    style = {},
    onClick
  },
  ref
) {
  const canvasRef = useRef(null);
  const mascotRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current) return;
    const instance = new JellyAlienMascot(canvasRef.current, {
      state,
      theme,
      squishFactor,
      followCursor
    });
    mascotRef.current = instance;
    return () => instance.destroy();
  }, [size]);

  useEffect(() => {
    if (mascotRef.current) mascotRef.current.setState(state);
  }, [state]);

  useEffect(() => {
    if (mascotRef.current) mascotRef.current.setTheme(theme);
  }, [theme]);

  useEffect(() => {
    if (mascotRef.current) mascotRef.current.squishFactor = squishFactor;
  }, [squishFactor]);

  useEffect(() => {
    if (mascotRef.current) mascotRef.current.followCursor = followCursor;
  }, [followCursor]);

  useImperativeHandle(ref, () => ({
    poke: (x, y, force) => mascotRef.current?.poke(x, y, force),
    setState: (s) => mascotRef.current?.setState(s),
    lookAt: (x, y) => mascotRef.current?.lookAt(x, y)
  }));

  return (
    <canvas
      ref={canvasRef}
      width={size}
      height={size}
      onClick={onClick}
      className={className}
      style={{ cursor: 'pointer', userSelect: 'none', ...style }}
    />
  );
});

export default JellyAlien;
