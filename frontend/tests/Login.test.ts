import { render, fireEvent, screen } from '@testing-library/svelte';
import Login from '../src/routes/login/+page.svelte';
import { goto } from '$app/navigation';
import { setToken } from '../src/stores';

// Mock the $app/navigation module
jest.mock('$app/navigation', () => ({
  goto: jest.fn(),
}));

// Mock the stores module
jest.mock('../src/stores', () => ({
  setToken: jest.fn(),
}));

describe('Login Component', () => {
  let fetchMock: jest.SpyInstance;

  beforeEach(() => {
    fetchMock = jest.spyOn(window, 'fetch').mockImplementation(jest.fn());
  });

  afterEach(() => {
    fetchMock.mockRestore();
  });

  it('renders login form', () => {
    render(Login);
    expect(screen.getByLabelText('Username:')).toBeInTheDocument();
    expect(screen.getByLabelText('Password:')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Login' })).toBeInTheDocument();
  });

  it('submits form with username and password', async () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ access_token: 'test_token' }),
    } as Response);

    render(Login);
    
    await fireEvent.input(screen.getByLabelText('Username:'), { target: { value: 'testuser' } });
    await fireEvent.input(screen.getByLabelText('Password:'), { target: { value: 'password123' } });
    await fireEvent.click(screen.getByRole('button', { name: 'Login' }));

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/auth/token',
      expect.objectContaining({
        method: 'POST',
        body: expect.any(URLSearchParams),
      })
    );
    expect(setToken).toHaveBeenCalledWith('test_token');
    expect(goto).toHaveBeenCalledWith('/chat');
  });

  it('displays error message on login failure', async () => {
    fetchMock.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Invalid credentials' }),
    } as Response);

    render(Login);
    
    await fireEvent.input(screen.getByLabelText('Username:'), { target: { value: 'testuser' } });
    await fireEvent.input(screen.getByLabelText('Password:'), { target: { value: 'wrongpassword' } });
    await fireEvent.click(screen.getByRole('button', { name: 'Login' }));

    expect(await screen.findByText('Invalid credentials')).toBeInTheDocument();
  });
});
