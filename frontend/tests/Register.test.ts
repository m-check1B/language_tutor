import { render, fireEvent, screen } from '@testing-library/svelte';
import Register from '../src/routes/register/+page.svelte';
import { goto } from '$app/navigation';

// Mock the $app/navigation module
jest.mock('$app/navigation', () => ({
  goto: jest.fn(),
}));

describe('Register Component', () => {
  let fetchMock: jest.SpyInstance;

  beforeEach(() => {
    fetchMock = jest.spyOn(window, 'fetch').mockImplementation(jest.fn());
  });

  afterEach(() => {
    fetchMock.mockRestore();
  });

  it('renders register form', () => {
    render(Register);
    expect(screen.getByLabelText('Username:')).toBeInTheDocument();
    expect(screen.getByLabelText('Email:')).toBeInTheDocument();
    expect(screen.getByLabelText('Password:')).toBeInTheDocument();
    expect(screen.getByLabelText('Confirm Password:')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Register' })).toBeInTheDocument();
  });

  it('submits form with valid data', async () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ username: 'testuser', email: 'test@example.com' }),
    } as Response);

    render(Register);
    
    await fireEvent.input(screen.getByLabelText('Username:'), { target: { value: 'testuser' } });
    await fireEvent.input(screen.getByLabelText('Email:'), { target: { value: 'test@example.com' } });
    await fireEvent.input(screen.getByLabelText('Password:'), { target: { value: 'password123' } });
    await fireEvent.input(screen.getByLabelText('Confirm Password:'), { target: { value: 'password123' } });
    await fireEvent.click(screen.getByRole('button', { name: 'Register' }));

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/auth/register',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'testuser',
          email: 'test@example.com',
          password: 'password123',
        }),
      })
    );
    expect(goto).toHaveBeenCalledWith('/login');
  });

  it('displays error message on registration failure', async () => {
    fetchMock.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Username already registered' }),
    } as Response);

    render(Register);
    
    await fireEvent.input(screen.getByLabelText('Username:'), { target: { value: 'existinguser' } });
    await fireEvent.input(screen.getByLabelText('Email:'), { target: { value: 'existing@example.com' } });
    await fireEvent.input(screen.getByLabelText('Password:'), { target: { value: 'password123' } });
    await fireEvent.input(screen.getByLabelText('Confirm Password:'), { target: { value: 'password123' } });
    await fireEvent.click(screen.getByRole('button', { name: 'Register' }));

    expect(await screen.findByText('Username already registered')).toBeInTheDocument();
  });

  it('displays error when passwords do not match', async () => {
    render(Register);
    
    await fireEvent.input(screen.getByLabelText('Username:'), { target: { value: 'testuser' } });
    await fireEvent.input(screen.getByLabelText('Email:'), { target: { value: 'test@example.com' } });
    await fireEvent.input(screen.getByLabelText('Password:'), { target: { value: 'password123' } });
    await fireEvent.input(screen.getByLabelText('Confirm Password:'), { target: { value: 'password456' } });
    await fireEvent.click(screen.getByRole('button', { name: 'Register' }));

    expect(await screen.findByText('Passwords do not match.')).toBeInTheDocument();
  });
});
