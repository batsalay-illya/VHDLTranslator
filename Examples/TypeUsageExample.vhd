library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity TypeUsage is
    Port (
        clk    : in  STD_LOGIC;
        reset  : in  STD_LOGIC;
        mode   : in  STD_LOGIC; -- 0 = normal, 1 = special mode
        output : out STD_LOGIC -- Single output signal
    );
end TypeUsage;

architecture Behavioral of TypeUsage is

    -- Declare a custom type for states
    type state_type is (STATE_A, STATE_B, STATE_C);
    signal current_state, next_state : state_type;

begin
    -- Single process for state transitions and output logic
    process(clk, reset)
    begin
        if reset = '1' then
            -- Reset state to STATE_A
            current_state <= STATE_A;
            output <= '0'; -- Default output on reset
        elsif rising_edge(clk) then
            -- Transition to the next state
            current_state <= next_state;
        end if;

        -- Output and next state logic
        case current_state is
            when STATE_A =>
                output <= '0'; -- Output for STATE_A
                if mode = '1' then
                    next_state <= STATE_C; -- Special mode skips to STATE_C
                else
                    next_state <= STATE_B;
                end if;

            when STATE_B =>
                output <= '1'; -- Output for STATE_B
                next_state <= STATE_C;

            when STATE_C =>
                output <= '0'; -- Output for STATE_C
                next_state <= STATE_A;

            when others =>
                next_state <= STATE_A; -- Default state
        end case;
    end process;

end Behavioral;
