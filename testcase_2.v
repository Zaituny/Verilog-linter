module test2 ( //Non-Full,Non-Parallel,Unreachable FSM State
input  wire        button_0 , button_1 ,
input  wire        rst,
input  wire        clk,
output reg         unlock
);



localparam [2:0]    IDLE = 3'b000,
                     S1 = 3'b001,
                     S2 = 3'b011,
					 S3 = 3'b010,
					 S4 = 3'b110,
					 UNLOCK = 3'b111;
					 
localparam [3:0]	 S5 = 4'b1010;
					 
reg [2:0]         current_state,
                     next_state ;
		
// state transition 		
always @(posedge clk or negedge rst)
 begin
  if(!rst)
   begin
     current_state <= IDLE ;
   end
  else
   begin
     current_state <= next_state ;
   end
 end
 
// next_state logic
always @(*)
 begin
  case(current_state)
  IDLE     : begin
              if(button_0)
			   next_state = IDLE ;
			  else if (button_1)
               next_state = S1 ;
              else
               next_state = IDLE ;			  
             end
  S1       : begin
              if(button_0)
			   next_state = IDLE ;
			  else if (button_1)
               next_state = S2 ;
              else
               next_state = S1 ;	   
            end
  S2     : begin
              if(button_0)
			   next_state = S3 ;
			  else if (button_1)
               next_state = IDLE ;
              else
               next_state = S2 ;	    
            end
  S3    : begin
              if(button_0)
			   next_state = IDLE ;
			  else if (button_1)
               next_state = S4 ;
              else
               next_state = S3 ;	    
            end
  S4   : begin
             if(button_0)
			   next_state = S5 ;
		     else if (button_1)
               next_state = IDLE ;
             else
               next_state = S4 ;	   
            end
  S5   : begin
             if(button_0)
			   next_state = UNLOCK ;
		     else if (button_1)
               next_state = IDLE ;
             else
               next_state = S5 ;	   
            end			
  UNLOCK  : begin
               next_state = IDLE ;
            end
  endcase
end	


// next_state logic
always @(*)
 begin
  case(current_state)
  IDLE     : begin
              unlock   =  1'b0 ;		  
             end
  S1       : begin
              unlock   =  1'b0 ;
             end	
  S2      : begin
              unlock   =  1'b0 ;	   
             end
  S3     : begin
              unlock   =  1'b0 ;	   
             end
  S3    : begin
              unlock   =  1'b0 ;		   
             end
  S5    : begin
              unlock   =  1'b0 ;		   
             end			 			 
  UNLOCK   : begin
              unlock   =  1'b1 ;	
             end				  
  endcase
 end	
		
		
endmodule					 