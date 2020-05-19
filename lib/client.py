"""
Make ranger as a client to neovim

"""
import os
import pynvim


class Client():
    """
    Ranger client for RPC

    """

    def __init__(self):
        self.nvim = None

    def attach_nvim(self):
        """
        Attach neovim session by socket path.

        """
        socket_path = os.getenv('NVIM_LISTEN_ADDRESS')

        if socket_path:
            self.nvim = pynvim.attach('socket', path=socket_path)

    def hide_window(self):
        """
        Hide the floating window.

        """
        self.nvim.call('rnvimr#rpc#enable_attach_file', async_=True)
        self.nvim.request('nvim_win_close', 0, 1, async_=True)

    def set_winhl(self, winhl):
        """
        Set the floating window highlight.

        :param winhl str: variable in ranger buffer
        """
        self.nvim.call('rnvimr#rpc#set_winhl', winhl)

    def rpc_edit(self, files, split=None, start_line=1):
        """
        Edit ranger target files in neovim though RPC.

        :param files list: list of file name
        :param split str: neovim split command
        :param start_line int: start line number
        """

        if not files:
            return

        try:
            pick_enable = self.nvim.vars['rnvimr_pick_enable']
        except KeyError:
            pick_enable = 0
        cmd = []
        if pick_enable:
            cmd.append('close')
        else:
            cmd.append('let cur_tab = nvim_get_current_tabpage()')
            cmd.append('let cur_win = nvim_get_current_win()')
            cmd.append('noautocmd wincmd p')
        if split:
            cmd.append('if bufname("%") != ""')
            cmd.append(split)
            cmd.append('endif')
            cmd.append('silent! edit {}'.format(files[0]))
        else:
            for file in files:
                cmd.append('noautocmd silent! edit +normal\\ {}zt {}'.format(start_line, file))
            cmd[-1] = cmd[-1].replace('noautocmd ', '', 1)

        if pick_enable:
            cmd.append('call rnvimr#rpc#enable_attach_file()')
        else:
            cmd.append('call rnvimr#rpc#buf_checkpoint()')
            cmd.append('if cur_tab != nvim_get_current_tabpage()')
            cmd.append('noautocmd call nvim_win_close(cur_win, 0)')
            cmd.append('noautocmd call rnvimr#toggle()')
            cmd.append('else')
            cmd.append('noautocmd call nvim_set_current_win(cur_win)')
            cmd.append('endif')
            cmd.append('noautocmd startinsert')
            cmd.append('unlet cur_tab')
            cmd.append('unlet cur_win')

        self.nvim.command('|'.join(cmd), async_=True)