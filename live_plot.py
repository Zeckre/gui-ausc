"""Realtime plotting helper for CTk apps.

Provides RealtimePlotController which embeds a matplotlib Figure into a
Tk parent widget and updates it either from an ADS1115 ADC (if available)
or from a simulated sine+noise signal.
"""
import time
import math
import random

# Try matplotlib
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except Exception:
    Figure = None
    FigureCanvasTkAgg = None
    MATPLOTLIB_AVAILABLE = False

# Try ADC
try:
    import Adafruit_ADS1x15
    ADC_AVAILABLE = True
except Exception:
    Adafruit_ADS1x15 = None
    ADC_AVAILABLE = False


class RealtimePlotController:
    def __init__(self, parent):
        if not MATPLOTLIB_AVAILABLE:
            raise RuntimeError("matplotlib/TkAgg not available")
        self.parent = parent
        self.fig = Figure(figsize=(6.4, 3.6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylim(0, 3)
        self.ax.set_xlim(0, 10)
        self.ax.set_xlabel("Tiempo (segundos)")
        self.ax.set_ylabel("Voltaje (V)")
        self.ax.set_title("Lectura ADC ADS1115 en Tiempo Real")
        self.ax.grid(True)

        (self.line,) = self.ax.plot([], [], lw=1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # data
        self.time_data = []
        self.voltage_data = []
        self.start_time = time.time()
        self._running = False
        self._after_id = None
        self._sample_count = 0

        # ADC setup if available
        self.GAIN = 1
        self.VOLTAGE_FSR = 4.096
        self.MAX_VALUE_16BIT = 32767
        if ADC_AVAILABLE:
            try:
                self.adc = Adafruit_ADS1x15.ADS1115(busnum=1)
            except Exception:
                self.adc = None
        else:
            self.adc = None
        # diagnostics
        try:
            print(f"RealtimePlotController init: MATPLOTLIB_AVAILABLE={MATPLOTLIB_AVAILABLE}, ADC_AVAILABLE={ADC_AVAILABLE}, adc_initialized={self.adc is not None}")
        except Exception:
            pass

    def _read_voltage(self):
        if self.adc is not None:
            try:
                value = self.adc.read_adc(0, gain=self.GAIN, data_rate=860)
                voltage = value * (self.VOLTAGE_FSR / self.MAX_VALUE_16BIT)
                return voltage
            except Exception:
                try:
                    print("RealtimePlotController: ADC read failed, falling back to simulation", flush=True)
                except Exception:
                    pass
                # fall through to simulated
                pass
        t = time.time() - self.start_time
        return 1.5 + 0.8 * math.sin(2 * math.pi * 0.5 * t) + (random.random() - 0.5) * 0.05

    def start(self, interval_ms=50, sample_interval_ms=None, plot_interval_ms=None):
        """Start sampling and plotting. Use either `interval_ms` or named `sample_interval_ms`/`plot_interval_ms`.
        """
        if self._running:
            return
        # start two loops: sampling (fast) and plotting (slower)
        self._running = True
        self._sample_after_id = None
        self._plot_after_id = None
        # determine intervals
        if sample_interval_ms is None and plot_interval_ms is None:
            self._sample_interval_ms = interval_ms
            self._plot_interval_ms = max(100, interval_ms * 4)
        else:
            self._sample_interval_ms = sample_interval_ms or interval_ms
            self._plot_interval_ms = plot_interval_ms or max(100, self._sample_interval_ms * 4)
        try:
            print(f"RealtimePlotController.start: sampling={self._sample_interval_ms}ms, plotting={self._plot_interval_ms}ms")
        except Exception:
            pass
        # ensure at least one plot is drawn immediately so user sees the axes
        try:
            self.canvas.draw_idle()
        except Exception:
            pass
        self._schedule_sample()
        self._schedule_plot()

    def stop(self):
        self._running = False
        for aid in (getattr(self, "_sample_after_id", None), getattr(self, "_plot_after_id", None)):
            if aid is not None:
                try:
                    self.parent.after_cancel(aid)
                except Exception:
                    pass
        self._sample_after_id = None
        self._plot_after_id = None

    def _schedule_sample(self):
        if not self._running:
            return
        # schedule next sample
        self._sample_after_id = self.parent.after(self._sample_interval_ms, self._sample)

    def _sample(self):
        # perform one reading and enqueue it
        try:
            current_time = time.time() - self.start_time
            voltage = self._read_voltage()
            self.time_data.append(current_time)
            self.voltage_data.append(voltage)
            # limit buffer length indirectly by time in plot stage
            # diagnostics: occasionally print a sample for debugging
            try:
                self._sample_count += 1
                if self._sample_count % 20 == 0:
                    print(f"RealtimePlotController.sample #{self._sample_count}: voltage={voltage:.4f}")
            except Exception:
                pass
        except Exception:
            try:
                print("RealtimePlotController._sample: exception", flush=True)
            except Exception:
                pass
        finally:
            self._schedule_sample()

    def _schedule_plot(self):
        if not self._running:
            return
        self._plot_after_id = self.parent.after(self._plot_interval_ms, self._plot_update)

    def _plot_update(self):
        if not self._running:
            return
        try:
            if not self.time_data:
                return
            current_time = time.time() - self.start_time
            # keep only last ~12 seconds
            while self.time_data and (current_time - self.time_data[0]) > 12:
                self.time_data.pop(0)
                self.voltage_data.pop(0)

            self.line.set_data(self.time_data, self.voltage_data)
            if current_time >= 10:
                self.ax.set_xlim(current_time - 10, current_time + 1)
            else:
                self.ax.set_xlim(0, 10)

            try:
                # draw once per plot interval
                self.canvas.draw_idle()
            except Exception:
                pass
        finally:
            self._schedule_plot()
