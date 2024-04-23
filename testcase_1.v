module calculator(//test1 :Arithmetic overflow, uninitialized register, Multi-driven bus/register
input wire op1,
input wire op2,
input wire op3,
input wire op4,
input wire clock,
input wire [2:0] in1,
input wire [2:0] in2,
output reg [2:0] out
);

reg [2:0] temp1;
reg [2:0] temp2;

always @(posedge clock)
begin
temp1 = 4'b0000;
if(op1)
begin
out = 3'b001 + 3'b111;
end
else if(op2)
begin
out = 4'b1000 - 3'b000;
end
else if(op3)
begin
out = temp1 << 1; 
end
else
begin
out = 4'b0000;
end
end

always @(*)
begin
temp1 = in1;
if(op4)
begin
out = temp1 >> 1;
end
else
begin
out = 3'b000;
end
end
endmodule
